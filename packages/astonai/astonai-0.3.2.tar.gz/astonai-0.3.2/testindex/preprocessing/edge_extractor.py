"""
Edge extraction utilities for Knowledge Graph.

This module provides utilities for extracting edges (relationships)
between nodes in the Knowledge Graph based on AST analysis of code chunks.
"""
import os
import sys
import ast
import json
import time
import fnmatch
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from testindex.core.config import ConfigModel
from testindex.core.path_resolution import PathResolver
from testindex.core.logging import get_logger
from testindex.preprocessing.ast_tools import extract_imports, extract_calls, CallVisitor, ImportVisitor
from testindex.preprocessing.parsing.ast_parser import ASTParser
from testindex.knowledge.schema.relationships import ImportsRelationship, CallsRelationship

# Default exclude patterns for common directories that should be ignored
DEFAULT_EXCLUDES = [
    "venv*/**",
    ".venv*/**", 
    "env/**",
    ".env/**",
    "node_modules/**",
    ".git/**",
    ".svn/**",
    ".hg/**",
    "__pycache__/**",
    "*.pyc",
    ".pytest_cache/**",
    ".coverage/**",
    "htmlcov/**",
    "build/**",
    "dist/**",
    "*.egg-info/**",
    ".tox/**",
    ".mypy_cache/**",
    ".idea/**",
    ".vscode/**",
    "*.min.js",
    "*.bundle.js"
]

# Set up logger
logger = get_logger(__name__)


class EdgeExtractionError(Exception):
    """Raised when there's an error during edge extraction."""
    pass


class EdgeExtractor:
    """Extract edges (function calls, imports) from code chunks."""
    
    def __init__(self, config: Optional[ConfigModel] = None, 
                repo_path: Optional[Union[str, Path]] = None,
                include_patterns: Optional[List[str]] = None,
                exclude_patterns: Optional[List[str]] = None):
        """Initialize the edge extractor.
        
        Args:
            config: Configuration model instance (optional)
            repo_path: Repository path (optional, defaults to current repo)
            include_patterns: List of glob patterns to include
            exclude_patterns: List of glob patterns to exclude
        """
        self.config = config
        self.repo_path = Path(repo_path) if repo_path else PathResolver.repo_root()
        self.ast_parser = ASTParser(config) if config else None
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        
        # Cache for node lookups
        self.module_node_map = {}  # name -> id
        self.function_node_map = {}  # name -> id
        self.chunk_id_map = {}  # chunk_id -> node_id
        
    def _should_process_file(self, source_file: str) -> bool:
        """Determine if a file should be processed based on include/exclude patterns.
        
        Args:
            source_file: File path to check
            
        Returns:
            True if the file should be processed, False otherwise
        """
        # Convert absolute path to relative path for pattern matching
        repo_root_str = str(self.repo_path)
        if source_file.startswith(repo_root_str):
            # Convert to relative path
            relative_path = source_file[len(repo_root_str):].lstrip(os.sep)
        else:
            # If not under repo_root, just use the path as is
            relative_path = source_file
        
        # Apply default excludes first
        for pattern in DEFAULT_EXCLUDES:
            if fnmatch.fnmatch(relative_path, pattern):
                return False
        
        # Apply custom exclude patterns
        if self.exclude_patterns:
            for pattern in self.exclude_patterns:
                if fnmatch.fnmatch(relative_path, pattern):
                    return False
        
        # If no include patterns, include all files that passed exclude filters
        if not self.include_patterns:
            return True
        
        # Check include patterns
        for pattern in self.include_patterns:
            if fnmatch.fnmatch(relative_path, pattern):
                return True
        
        # File doesn't match any include pattern
        return False
    
    def extract_edges(self, 
                     chunks_file: Optional[Union[str, Path]] = None, 
                     nodes_file: Optional[Union[str, Path]] = None,
                     output_file: Optional[Union[str, Path]] = None) -> Dict[str, int]:
        """Extract edges from chunks and write to output file.
        
        Args:
            chunks_file: Path to the chunks.json file (optional)
            nodes_file: Path to the nodes.json file (optional)
            output_file: Path to write the edges.json file (optional)
            
        Returns:
            Dict with edge counts by type
        """
        start_time = time.time()
        
        # Use default paths if not provided
        if chunks_file is None:
            chunks_file = PathResolver.knowledge_graph_dir() / "chunks.json"
        if nodes_file is None:
            nodes_file = PathResolver.knowledge_graph_dir() / "nodes.json"
        if output_file is None:
            output_file = PathResolver.edges_file()
            
        chunks_file = Path(chunks_file)
        nodes_file = Path(nodes_file)
        output_file = Path(output_file)
        
        logger.info(f"Extracting edges from {chunks_file} and {nodes_file}")
        logger.info(f"Output will be written to {output_file}")
        
        # Ensure required input files exist
        if not chunks_file.exists():
            raise EdgeExtractionError(f"Chunks file not found: {chunks_file}")
        if not nodes_file.exists():
            raise EdgeExtractionError(f"Nodes file not found: {nodes_file}")
        
        # Load chunks and nodes
        chunks, nodes = self._load_data(chunks_file, nodes_file)
        
        # Build lookup maps for efficient edge generation
        self._build_lookup_maps(nodes)
        
        # Extract edges
        edges = []
        edges_set = set()  # For deduplication
        call_count = 0
        import_count = 0
        processed_file_count = 0
        skipped_file_count = 0
        
        # Debug: Check module and function maps
        logger.debug(f"Module node map has {len(self.module_node_map)} entries")
        logger.debug(f"Function node map has {len(self.function_node_map)} entries")
        logger.debug(f"Chunk ID map has {len(self.chunk_id_map)} entries")
        
        # Process chunks to extract edges
        # Note: chunk_type in chunks.json is lowercase (e.g., 'module', 'function', 'method')
        # but they were previously checked for uppercase (e.g., 'MODULE', 'FUNCTION'), causing no edges to be found
        chunk_counts = {"module": 0, "function": 0, "method": 0, "nested_function": 0, "standalone_code": 0, "other": 0}
        
        # Track unique files for accurate file counts
        processed_files = set()
        
        for i, chunk in enumerate(chunks):
            source_file = chunk.get('source_file', '')
            chunk_type = chunk.get('chunk_type', '').lower()  # Normalize to lowercase

            # Debug: Log chunk types
            if i < 5 or i % 100 == 0:  # Log first 5 and every 100th after that
                logger.debug(f"Processing chunk {i}: type={chunk_type}, file={source_file}")

            # Count chunk types
            if chunk_type in chunk_counts:
                chunk_counts[chunk_type] += 1
            else:
                chunk_counts["other"] += 1
                if i < 10:  # Only log the first few unknown types
                    logger.debug(f"Unknown chunk type: {chunk_type}")

            # Skip files based on include/exclude patterns
            if not self._should_process_file(source_file):
                if source_file not in processed_files:
                    skipped_file_count += 1
                    processed_files.add(source_file)  # Mark as seen even though skipped
                continue

            # Track unique processed files
            if source_file not in processed_files:
                processed_file_count += 1
                processed_files.add(source_file)

            if chunk_type == 'standalone_code':
                continue

            # Process imports for module chunks
            if chunk_type == 'module':
                import_edges = self._extract_import_edges(chunk)
                for edge in import_edges:
                    edge_key = f"{edge['src']}:IMPORTS:{edge['dst']}"
                    if edge_key not in edges_set:
                        edges.append(edge)
                        edges_set.add(edge_key)
                import_count += len(import_edges)

            # Process function calls
            if chunk_type in ('function', 'method', 'nested_function'):
                call_edges = self._extract_call_edges(chunk)
                for edge in call_edges:
                    edge_key = f"{edge['src']}:CALLS:{edge['dst']}"
                    if edge_key not in edges_set:
                        edges.append(edge)
                        edges_set.add(edge_key)
                call_count += len(call_edges)
        
        # Debug: Log chunk type counts
        logger.debug(f"Chunk type counts: {chunk_counts}")
        logger.info(f"Processed {processed_file_count} files, skipped {skipped_file_count} files")
        
        # Write edges to file
        self._write_edges(edges, output_file)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Get parsing statistics
        parsing_stats = self.get_parsing_stats()
        
        # Log summary
        logger.info(f"Extracted {len(edges)} edges ({call_count} CALLS, {import_count} IMPORTS) in {duration:.2f}s")
        
        return {
            "total": len(edges),
            "CALLS": call_count,
            "IMPORTS": import_count,
            "processed_files": processed_file_count,
            "skipped_files": skipped_file_count,
            "duration": duration,
            "parsing_stats": parsing_stats
        }
    
    def _load_data(self, chunks_file: Path, nodes_file: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load chunks and nodes from JSON files.
        
        Args:
            chunks_file: Path to chunks.json
            nodes_file: Path to nodes.json
            
        Returns:
            Tuple of (chunks, nodes) lists
        """
        try:
            with open(chunks_file, 'r') as f:
                chunks = json.load(f)
            logger.info(f"Loaded {len(chunks)} chunks from {chunks_file}")
        except Exception as e:
            raise EdgeExtractionError(f"Failed to load chunks: {str(e)}")
            
        try:
            with open(nodes_file, 'r') as f:
                nodes = json.load(f)
            logger.info(f"Loaded {len(nodes)} nodes from {nodes_file}")
        except Exception as e:
            raise EdgeExtractionError(f"Failed to load nodes: {str(e)}")
            
        return chunks, nodes
    
    def _build_lookup_maps(self, nodes: List[Dict[str, Any]]) -> None:
        """Build lookup maps for node IDs by name.
        
        Args:
            nodes: List of node dictionaries
        """
        # Reset maps
        self.module_node_map = {}
        self.function_node_map = {}
        self.chunk_id_map = {}
        
        module_count = 0
        function_count = 0
        chunk_id_count = 0
        
        logger.debug(f"Building lookup maps from {len(nodes)} nodes")
        
        # Build maps
        for node in nodes:
            node_id = node.get('id', '')
            if not node_id:
                logger.debug(f"Skipping node without ID: {node}")
                continue
                
            # Store chunk_id to node_id mapping if available
            chunk_id = None
            if 'properties' in node and isinstance(node['properties'], dict):
                chunk_id = node['properties'].get('chunk_id')
            elif 'properties' in node and isinstance(node['properties'], str):
                try:
                    props = json.loads(node['properties'])
                    chunk_id = props.get('chunk_id')
                except:
                    logger.debug(f"Could not parse properties as JSON for node {node_id}")
                    pass
                    
            if chunk_id:
                self.chunk_id_map[chunk_id] = node_id
                chunk_id_count += 1
            
            # Store by node type and name
            node_type = node.get('type', '')
            node_name = node.get('name', '')
            
            if node_type == 'Module' and node_name:
                self.module_node_map[node_name] = node_id
                module_count += 1
                logger.debug(f"Added module mapping: {node_name} -> {node_id}")
                
            if node_type == 'Implementation' and node_name:
                # Store both simple name and fully qualified name
                self.function_node_map[node_name] = node_id
                function_count += 1
                logger.debug(f"Added function mapping: {node_name} -> {node_id}")
                
                # If it's a qualified name (contains dots), also store the simple name
                name_parts = node_name.split('.')
                if len(name_parts) > 1:
                    simple_name = name_parts[-1]
                    # Only store if not already present to avoid conflicts
                    if simple_name not in self.function_node_map:
                        self.function_node_map[simple_name] = node_id
                        logger.debug(f"Added simple function name mapping: {simple_name} -> {node_id}")
        
        logger.debug(f"Built lookup maps: {module_count} modules, {function_count} functions, {chunk_id_count} chunk IDs")
    
    def _extract_import_edges(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract import edges from a module chunk.
        
        Args:
            chunk: Module chunk dictionary
            
        Returns:
            List of edge dictionaries
        """
        edges = []
        
        # Skip if no source code
        source = chunk.get('source', chunk.get('source_code', ''))
        if not source:
            logger.debug(f"Skipping chunk {chunk.get('chunk_id', 'unknown')}: No source code")
            return edges
        
        # Skip if no chunk_id
        chunk_id = chunk.get('chunk_id')
        if not chunk_id:
            logger.debug(f"Skipping chunk: No chunk_id found")
            return edges
            
        # Get source node ID
        source_id = f"module_{chunk_id}"
        if chunk_id in self.chunk_id_map:
            source_id = self.chunk_id_map[chunk_id]
        
        logger.debug(f"Processing module chunk {chunk_id} with source ID {source_id}")
        
        try:
            # Use robust parsing
            if self.ast_parser:
                tree = self.ast_parser.parse_source_robust(source, chunk.get('source_file'))
            else:
                tree = ast.parse(source)
            
            if tree is None:
                logger.warning(f"Could not parse {chunk.get('source_file', '<unknown>')}")
                return edges
                
            # Extract imports (fallback parsers don't extract imports, so use standard method)
            imports = extract_imports(tree)
            logger.debug(f"Extracted {len(imports)} imports from chunk {chunk_id}: {imports}")
            
            # Create import edges
            for import_name in imports:
                # Try different variations of the import name for matching
                matches = self._find_matching_module(import_name)
                
                if matches:
                    for target_id in matches:
                        edges.append({
                            "type": "IMPORTS",
                            "src": source_id,
                            "dst": target_id
                        })
                        logger.debug(f"Created IMPORTS edge: {source_id} -> {target_id} ({import_name})")
                else:
                    logger.debug(f"Could not find module node for import: {import_name}")
        
        except Exception as e:
            logger.warning(f"Error extracting imports from {chunk.get('source_file', '<unknown>')}: {e}")
            
        return edges
    
    def _extract_call_edges(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function call edges from a function chunk.
        
        Args:
            chunk: Function chunk dictionary
            
        Returns:
            List of edge dictionaries
        """
        edges = []
        
        # Skip if no source code
        source = chunk.get('source', chunk.get('source_code', ''))
        if not source:
            logger.debug(f"Skipping chunk {chunk.get('chunk_id', 'unknown')}: No source code")
            return edges
        
        # Skip if no chunk_id
        chunk_id = chunk.get('chunk_id')
        if not chunk_id:
            logger.debug(f"Skipping chunk: No chunk_id found")
            return edges
            
        # Get source node ID
        source_id = f"impl_{chunk_id}"
        if chunk_id in self.chunk_id_map:
            source_id = self.chunk_id_map[chunk_id]
        
        logger.debug(f"Processing function chunk {chunk_id} with source ID {source_id}")
        
        try:
            # Use robust parsing
            if self.ast_parser:
                logger.debug(f"Using robust parser for {chunk.get('source_file')}")
                tree = self.ast_parser.parse_source_robust(source, chunk.get('source_file'))
            else:
                logger.debug(f"Using standard AST parser for {chunk.get('source_file')}")
                tree = ast.parse(source)
            
            if tree is None:
                logger.warning(f"Could not parse {chunk.get('source_file', '<unknown>')}")
                return edges
            
            # Extract calls based on parsing strategy used
            calls = []
            if hasattr(tree, '_parso_calls'):
                calls = tree._parso_calls
                logger.debug(f"Using parso calls: {calls}")
            elif hasattr(tree, '_libcst_calls'):
                calls = tree._libcst_calls
                logger.debug(f"Using libcst calls: {calls}")
            elif hasattr(tree, '_regex_calls'):
                calls = tree._regex_calls
                logger.debug(f"Using regex calls: {calls}")
            else:
                # Standard AST extraction
                calls = extract_calls(tree)
                logger.debug(f"Using standard AST calls: {calls}")
            
            logger.debug(f"Extracted {len(calls)} calls from chunk {chunk_id}: {calls}")
            
            # Create call edges
            for call_name in calls:
                # Skip method calls on variables (we can't resolve these)
                if '.' in call_name and not self._is_qualified_function(call_name):
                    logger.debug(f"Skipping unresolvable method call: {call_name}")
                    continue
                    
                # Try different variations of the call name for matching
                matches = self._find_matching_function(call_name)
                
                if matches:
                    for target_id in matches:
                        edges.append({
                            "type": "CALLS",
                            "src": source_id,
                            "dst": target_id
                        })
                        logger.debug(f"Created CALLS edge: {source_id} -> {target_id} ({call_name})")
                else:
                    logger.debug(f"Could not find function node for call: {call_name}")
        
        except Exception as e:
            logger.warning(f"Error extracting calls from {chunk.get('source_file', '<unknown>')}: {e}")
            
        return edges
    
    def _find_matching_module(self, import_name: str) -> List[str]:
        """Find matching module nodes for a given import name.
        
        The matching algorithm uses several strategies to handle common cases:
        1. Direct match: The import name exactly matches a module node
        2. Partial match: The import is a parent or submodule of modules in the graph
        
        Args:
            import_name: Import name to match
            
        Returns:
            List of matching node IDs
        """
        matches = []
        
        # Check for direct match
        if import_name in self.module_node_map:
            matches.append(self.module_node_map[import_name])
        
        # Check for partial matches (e.g., 'flask' matches 'flask.app')
        for name, node_id in self.module_node_map.items():
            # Check if the import is a submodule or a parent module
            if import_name.startswith(name + '.') or name.startswith(import_name + '.'):
                if node_id not in matches:
                    matches.append(node_id)
        
        return matches
    
    def _find_matching_function(self, call_name: str) -> List[str]:
        """Find matching function nodes for a given call name.
        
        The matching algorithm uses several strategies to handle common cases:
        1. Direct match: The call name exactly matches a function node
        2. Method name match: For method calls (e.g., obj.method), match just the method name
        3. Partial qualified name match: Match based on the last segments of the qualified name
        
        Args:
            call_name: Function call name to match
            
        Returns:
            List of matching node IDs
        """
        matches = []
        
        # Check for direct match
        if call_name in self.function_node_map:
            matches.append(self.function_node_map[call_name])
            return matches
        
        # For method calls (e.g., obj.method()), try to match just the method name
        if '.' in call_name:
            simple_name = call_name.split('.')[-1]
            if simple_name in self.function_node_map:
                matches.append(self.function_node_map[simple_name])
        
        # Check for partial qualified name matches
        for name, node_id in self.function_node_map.items():
            if '.' in name and '.' in call_name:
                # For qualified names, check if the last parts match
                # (e.g., 'flask.request.get_json' could match 'request.get_json')
                name_parts = name.split('.')
                call_parts = call_name.split('.')
                
                # Compare the last 1 or 2 segments
                if name_parts[-1] == call_parts[-1]:
                    if len(name_parts) >= 2 and len(call_parts) >= 2 and name_parts[-2] == call_parts[-2]:
                        # 2-segment match is stronger
                        if node_id not in matches:
                            matches.append(node_id)
                    elif node_id not in matches:
                        # 1-segment match is weaker but still valid
                        matches.append(node_id)
        
        return matches
    
    def _is_qualified_function(self, name: str) -> bool:
        """Check if a name is a qualified function name (e.g., os.path.join).
        
        Args:
            name: Function name to check
            
        Returns:
            True if it's a qualified function name, False otherwise
        """
        parts = name.split('.')
        if len(parts) < 2:
            return False
            
        # Check if the base module exists
        base_module = parts[0]
        if base_module in self.module_node_map:
            return True
            
        # Check if the full name exists as a function
        if name in self.function_node_map:
            return True
            
        return False
    
    def _write_edges(self, edges: List[Dict[str, Any]], output_file: Path) -> None:
        """Write edges to output file.
        
        Args:
            edges: List of edge dictionaries
            output_file: Path to write edges.json
        """
        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create output data
        output_data = {
            "schema_version": "K1-E",
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "edges": edges
        }
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            logger.info(f"Wrote {len(edges)} edges to {output_file}")
        except Exception as e:
            raise EdgeExtractionError(f"Failed to write edges: {str(e)}")
            
    def get_parsing_stats(self) -> Dict[str, int]:
        """Get parsing statistics from the robust parser.
        
        Returns:
            Dictionary with parsing strategy counts
        """
        if self.ast_parser and hasattr(self.ast_parser, 'get_parsing_stats'):
            return self.ast_parser.get_parsing_stats()
        return {}
    
    @staticmethod
    def check_requirements() -> bool:
        """Check if all requirements for edge extraction are met.
        
        Returns:
            True if all requirements are met, False otherwise
        """
        # Check required Python packages
        try:
            import ast
            import json
            
            # Check if the knowledge graph directory exists
            kg_dir = PathResolver.knowledge_graph_dir()
            chunks_file = kg_dir / "chunks.json"
            nodes_file = kg_dir / "nodes.json"
            
            if not chunks_file.exists():
                logger.warning(f"Missing chunks.json file at {chunks_file}")
                return False
                
            if not nodes_file.exists():
                logger.warning(f"Missing nodes.json file at {nodes_file}")
                return False
                
            return True
        except ImportError as e:
            logger.warning(f"Missing dependency: {str(e)}")
            return False
        except Exception as e:
            logger.warning(f"Error checking requirements: {str(e)}")
            return False 