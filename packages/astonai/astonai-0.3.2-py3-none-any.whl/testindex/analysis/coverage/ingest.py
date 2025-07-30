"""
Coverage ingestion functionality.

This module provides functions to ingest coverage data from various formats
and update the knowledge graph nodes with coverage information.
"""

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
import logging

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver

# Set up logger
logger = get_logger(__name__)


def parse_coverage_xml(coverage_file: str) -> Dict[str, int]:
    """Parse coverage.xml file to extract coverage information.
    
    Args:
        coverage_file: Path to the coverage.xml file
        
    Returns:
        Dict mapping file_path:function_name to coverage percentage
    """
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Get overall coverage data
        overall_line_rate = float(root.get('line-rate', '0'))
        coverage_percent = int(100 - (overall_line_rate * 100))
        
        logger.info(f"Overall coverage rate from XML: {overall_line_rate}, gap: {coverage_percent}%")
        
        # Extract source dir from XML if available
        source_dirs = []
        sources_elem = root.find('sources')
        if sources_elem is not None:
            for source_elem in sources_elem.findall('source'):
                if source_elem.text:
                    source_dirs.append(source_elem.text)
                    logger.debug(f"Found source directory: {source_elem.text}")
        
        coverage_data = {}
        
        # Process each class (file) in the coverage report
        for class_elem in root.findall('.//class'):
            filename = class_elem.get('filename', '')
            if not filename:
                continue
                
            # If we have source directories, construct full path
            full_paths = []
            if source_dirs:
                for source_dir in source_dirs:
                    full_path = os.path.join(source_dir, filename)
                    # Convert to repository-relative path
                    repo_rel_path = PathResolver.to_repo_relative(full_path)
                    full_paths.append(repo_rel_path)
            else:
                # Ensure path is repository-relative
                repo_rel_path = PathResolver.to_repo_relative(filename)
                full_paths = [repo_rel_path]
                
            # Try to find line coverage information
            line_rate = float(class_elem.get('line-rate', '0'))
            file_coverage = int(100 - (line_rate * 100))
            
            # Store file-level coverage
            for path in full_paths:
                # Normalize the path for consistent matching
                norm_path = PathResolver.normalize_path(path)
                coverage_data[f"FILE:{norm_path}"] = file_coverage
                
                # For top-level paths without parent dir, also store by basename
                if '/' in norm_path:
                    basename = norm_path.split('/')[-1]
                    coverage_data[f"FILE:{basename}"] = file_coverage
            
            # Process methods for this class
            methods_elem = class_elem.find('methods')
            if methods_elem is not None:
                for method_elem in methods_elem.findall('method'):
                    method_name = method_elem.get('name', '')
                    if not method_name:
                        continue
                        
                    # Get method coverage
                    method_line_rate = float(method_elem.get('line-rate', '0'))
                    method_coverage = int(100 - (method_line_rate * 100))
                    
                    # Store method coverage for each possible path
                    for path in full_paths:
                        # Normalize the path for consistent matching
                        norm_path = PathResolver.normalize_path(path)
                        coverage_data[f"{norm_path}:{method_name}"] = method_coverage
                        
                        # Also store just by method name for fallback matching
                        if method_name not in coverage_data:
                            coverage_data[method_name] = method_coverage
            
            # If no methods found, add class-level coverage for each method found in the file
            # This handles the case where coverage.xml has empty methods tags
            else:
                for path in full_paths:
                    norm_path = PathResolver.normalize_path(path)
                    coverage_data[f"FILE:{norm_path}"] = file_coverage
        
        # If we didn't find any specific coverage data, but we have overall line rate,
        # create a placeholder entry to report the overall gap percentage
        if not coverage_data and coverage_percent > 0:
            coverage_data["OVERALL"] = coverage_percent
            
        logger.info(f"Extracted coverage data for {len(coverage_data)} entries")
        return coverage_data
            
    except Exception as e:
        logger.error(f"Failed to parse coverage XML: {str(e)}")
        return {}


def normalize_path(path: str, source_path: Optional[str] = None) -> str:
    """Normalize a file path by removing source prefix and ensuring consistent separators.
    
    Args:
        path: The file path to normalize
        source_path: The source path prefix to remove, if any
        
    Returns:
        Normalized path
    """
    # Use PathResolver for consistent path normalization
    return PathResolver.normalize_path(path)


def update_kg_nodes(kg_dir: str, coverage_data: Dict[str, int]) -> Tuple[int, int]:
    """Update knowledge graph nodes with coverage information.
    
    Args:
        kg_dir: Path to the knowledge graph directory
        coverage_data: Dictionary mapping functions to coverage percentage
        
    Returns:
        Tuple containing (number of updated nodes, total implementation nodes)
    """
    nodes_file = Path(kg_dir) / "nodes.json"
    
    if not nodes_file.exists():
        logger.error(f"Nodes file not found: {nodes_file}")
        return 0, 0
        
    logger.info(f"Updating coverage information in {nodes_file}")
    
    try:
        # Load nodes
        with open(nodes_file, 'r') as f:
            nodes = json.load(f)
            
        # Count implementations
        impl_count = sum(1 for node in nodes if node.get("type") == "Implementation")
        logger.info(f"Found {impl_count} Implementation nodes")
        
        # Update coverage information
        updated_count = 0
        for node in nodes:
            if node.get("type") == "Implementation":
                # Get the file path and ensure it's repository-relative
                file_path = node.get("file_path", "")
                if file_path:
                    # Update the node's file_path to be repository-relative
                    repo_rel_path = PathResolver.to_repo_relative(file_path)
                    if repo_rel_path != file_path:
                        node["file_path"] = repo_rel_path
                        logger.debug(f"Updated node file_path: {file_path} -> {repo_rel_path}")
                        file_path = repo_rel_path
                
                name = node.get("name", "")
                
                # Normalize file_path for consistent matching
                norm_file_path = PathResolver.normalize_path(file_path)
                
                # Create various keys to try matching
                key = f"{norm_file_path}:{name}"
                file_key = f"FILE:{norm_file_path}"
                
                # Ensure properties exists
                if "properties" not in node:
                    node["properties"] = {}
                
                # Debug info for the first few nodes or when extra debug enabled
                if updated_count < 5 or os.environ.get("DEBUG", "0") == "1":
                    logger.debug(f"Node path: {norm_file_path}")
                    logger.debug(f"Trying keys: {key}, {file_key}")
                
                # Try to find coverage using multiple strategies
                coverage_found = False
                
                # First try exact match
                if key in coverage_data:
                    node["properties"]["coverage"] = coverage_data[key]
                    updated_count += 1
                    coverage_found = True
                    if updated_count < 10 or os.environ.get("DEBUG", "0") == "1":
                        logger.debug(f"Found coverage with key: {key} = {coverage_data[key]}%")
                
                elif name in coverage_data:
                    node["properties"]["coverage"] = coverage_data[name]
                    updated_count += 1
                    coverage_found = True
                    if updated_count < 10 or os.environ.get("DEBUG", "0") == "1":
                        logger.debug(f"Found coverage with name: {name} = {coverage_data[name]}%")
                    
                elif file_key in coverage_data:
                    node["properties"]["coverage"] = coverage_data[file_key]
                    updated_count += 1
                    coverage_found = True
                    if updated_count < 10 or os.environ.get("DEBUG", "0") == "1":
                        logger.debug(f"Found coverage with file_key: {file_key} = {coverage_data[file_key]}%")
                    
                # Try fallback matching strategies using PathResolver
                elif not coverage_found:
                    coverage_paths = [k for k in coverage_data.keys() if k.startswith("FILE:")]
                    coverage_paths = [k[5:] for k in coverage_paths]  # Remove "FILE:" prefix
                    
                    matched_path = PathResolver.match_coverage_path(norm_file_path, coverage_paths)
                    if matched_path:
                        node["properties"]["coverage"] = coverage_data[f"FILE:{matched_path}"]
                        updated_count += 1
                        coverage_found = True
                        logger.debug(f"Found coverage with match_coverage_path: {matched_path} = {coverage_data[f'FILE:{matched_path}']}%")
                
                # If no coverage data found, explicitly set to 0
                if not coverage_found:
                    # Only default to 0 if we don't already have coverage data
                    if "coverage" not in node["properties"]:
                        node["properties"]["coverage"] = 0
                
        # Write updated nodes
        with open(nodes_file, 'w') as f:
            json.dump(nodes, f, indent=2)
            
        logger.info(f"Updated coverage information for {updated_count} nodes out of {impl_count} Implementation nodes")
        return updated_count, impl_count
            
    except Exception as e:
        logger.error(f"Failed to update coverage information: {e}")
        return 0, 0


def ingest_coverage(coverage_file: str, kg_dir: str) -> Tuple[int, int]:
    """Ingest coverage data and update knowledge graph.
    
    Args:
        coverage_file: Path to the coverage data file
        kg_dir: Path to the knowledge graph directory
        
    Returns:
        Tuple containing (number of updated nodes, total implementation nodes)
    """
    # Parse coverage data
    coverage_data = parse_coverage_xml(coverage_file)
    
    # Update knowledge graph nodes
    return update_kg_nodes(kg_dir, coverage_data)


def find_coverage_file() -> Optional[str]:
    """Find coverage.xml in the current directory or its subdirectories.
    
    Returns:
        Path to coverage.xml if found, None otherwise
    """
    # Use PathResolver to find coverage file
    coverage_file = PathResolver.find_coverage_file()
    if coverage_file:
        return str(coverage_file)
    return None


def has_coverage_data(kg_dir: str) -> bool:
    """Check if knowledge graph nodes already have coverage data.
    
    Args:
        kg_dir: Path to the knowledge graph directory
        
    Returns:
        True if any nodes have coverage data, False otherwise
    """
    # Convert kg_dir to Path if it's a string
    if isinstance(kg_dir, str):
        kg_dir = Path(kg_dir)
    
    # Get nodes file path
    nodes_file = kg_dir / "nodes.json"
    
    if not nodes_file.exists():
        logger.warning(f"Nodes file not found: {nodes_file}")
        return False
        
    try:
        with open(nodes_file, 'r') as f:
            nodes = json.load(f)
            
        found_coverage = False
        impl_count = 0
        
        for node in nodes:
            if node.get("type") == "Implementation":
                impl_count += 1
                props = node.get("properties", {})
                if "coverage" in props and props["coverage"] > 0:
                    found_coverage = True
                    logger.debug(f"Found coverage data in node: {node.get('name', 'unknown')}")
                    # Return early once we find coverage data
                    return True
                    
        if impl_count > 0 and not found_coverage:
            logger.warning(f"Found {impl_count} Implementation nodes but none have coverage data > 0")
            
        return found_coverage
        
    except Exception as e:
        logger.error(f"Error checking coverage data: {e}")
        return False 