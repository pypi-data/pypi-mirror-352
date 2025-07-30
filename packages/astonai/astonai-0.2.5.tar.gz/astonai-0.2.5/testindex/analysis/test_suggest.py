"""
Test Suggestion Engine for TestIndex.

This module generates test suggestions for implementation nodes based on
AST analysis and optionally LLM suggestions.
"""

import ast
import json
import os
import time
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Set
import traceback

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver

# Set up logger
logger = get_logger(__name__)


class SuggestionError(Exception):
    """Raised when there's an error during test suggestion generation."""
    pass


class SuggestionEngine:
    """Generates test suggestions for implementation nodes."""
    
    def __init__(self, llm_enabled: bool = False, model: str = "gpt-4o", budget: float = 0.03):
        """Initialize the test suggestion engine.
        
        Args:
            llm_enabled: Whether to use LLM for suggestions
            model: LLM model to use (if enabled)
            budget: Maximum cost per suggestion in dollars
        """
        self.llm_enabled = llm_enabled
        self.model = model
        self.budget = Decimal(str(budget))
        self.nodes_map = {}  # id -> node
        self.file_nodes_map = {}  # file_path -> [node_ids]
        
    def generate_suggestions(self, 
                            target: str,
                            nodes_file: Optional[Union[str, Path]] = None,
                            critical_path_file: Optional[Union[str, Path]] = None,
                            output_file: Optional[Union[str, Path]] = None,
                            k: int = 5) -> List[Dict[str, Any]]:
        """Generate test suggestions for the target file or node.
        
        Args:
            target: Path to file or fully-qualified node name
            nodes_file: Path to the nodes.json file (optional)
            critical_path_file: Path to the critical_path.json file (optional)
            output_file: Path to write the test_suggestions.json file (optional)
            k: Maximum number of suggestions to generate
            
        Returns:
            List of test suggestions
        """
        start_time = time.time()
        
        # Use default paths if not provided
        if nodes_file is None:
            nodes_file = PathResolver.nodes_file()
        if critical_path_file is None:
            critical_path_file = PathResolver.knowledge_graph_dir() / "critical_path.json"
        if output_file is None:
            output_file = PathResolver.knowledge_graph_dir() / "test_suggestions.json"
            
        nodes_file = Path(nodes_file)
        critical_path_file = Path(critical_path_file)
        output_file = Path(output_file)
        
        logger.info(f"Generating test suggestions for target: {target}")
        logger.info(f"Using nodes file: {nodes_file}")
        logger.info(f"Using critical path file (if exists): {critical_path_file}")
        logger.info(f"Output will be written to: {output_file}")
        
        # Ensure nodes file exists
        if not nodes_file.exists():
            raise SuggestionError(f"Nodes file not found: {nodes_file}")
            
        # Determine if target is a file path or node name
        is_file_path = os.path.exists(target) or '/' in target or '\\' in target
        
        # Load nodes
        nodes = self._load_nodes(nodes_file)
        
        # Build lookup maps
        self._build_lookup_maps(nodes)
        
        # Identify target nodes
        target_nodes = self._identify_target_nodes(target, is_file_path)
        
        if not target_nodes:
            raise SuggestionError(f"No matching nodes found for target: {target}")
        
        logger.info(f"Found {len(target_nodes)} target nodes")
        
        # If critical path file exists, use it to prioritize nodes
        critical_nodes = []
        if critical_path_file.exists():
            try:
                critical_nodes = self._load_critical_path(critical_path_file)
                logger.info(f"Loaded {len(critical_nodes)} critical nodes for prioritization")
            except Exception as e:
                logger.warning(f"Failed to load critical path data: {e}")
        
        # Prioritize target nodes based on critical path
        prioritized_nodes = self._prioritize_nodes(target_nodes, critical_nodes)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(prioritized_nodes, k)
        
        # Write to output file
        self._write_output(suggestions, output_file)
        
        # Calculate duration
        duration = time.time() - start_time
        logger.info(f"Test suggestion generation completed in {duration:.2f}s")
        logger.info(f"Generated {len(suggestions)} test suggestions")
        
        return suggestions
    
    def _load_nodes(self, nodes_file: Path) -> List[Dict[str, Any]]:
        """Load nodes from JSON file.
        
        Args:
            nodes_file: Path to nodes.json
            
        Returns:
            List of node dictionaries
        """
        try:
            with open(nodes_file, 'r') as f:
                nodes = json.load(f)
            logger.info(f"Loaded {len(nodes)} nodes from {nodes_file}")
            return nodes
        except Exception as e:
            raise SuggestionError(f"Failed to load nodes: {str(e)}")
    
    def _load_critical_path(self, critical_path_file: Path) -> List[Dict[str, Any]]:
        """Load critical path data from JSON file.
        
        Args:
            critical_path_file: Path to critical_path.json
            
        Returns:
            List of critical node dictionaries
        """
        try:
            with open(critical_path_file, 'r') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if isinstance(data, dict) and "nodes" in data:
                return data["nodes"]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected critical path data format: {type(data)}")
                return []
        except Exception as e:
            raise SuggestionError(f"Failed to load critical path data: {str(e)}")
    
    def _build_lookup_maps(self, nodes: List[Dict[str, Any]]) -> None:
        """Build lookup maps for nodes by ID and file path.
        
        Args:
            nodes: List of node dictionaries
        """
        # Build node ID map
        for node in nodes:
            node_id = node.get("id")
            if node_id:
                self.nodes_map[node_id] = node
                
                # Add to file path map
                file_path = node.get("file_path")
                if file_path:
                    # Normalize file path for consistent matching
                    norm_path = PathResolver.normalize_path(file_path)
                    
                    if norm_path not in self.file_nodes_map:
                        self.file_nodes_map[norm_path] = []
                    
                    self.file_nodes_map[norm_path].append(node_id)
    
    def _identify_target_nodes(self, target: str, is_file_path: bool) -> List[Dict[str, Any]]:
        """Identify nodes matching the target.
        
        Args:
            target: Path to file or fully-qualified node name
            is_file_path: Whether target is a file path
            
        Returns:
            List of matching node dictionaries
        """
        logger.debug(f"Identifying target nodes for: {target} (is_file_path={is_file_path})")
        
        # Special handling for qualified names (file_path::name format)
        if "::" in target:
            file_path, node_name = target.split("::", 1)
            # Search for nodes with matching file_path and name
            matching_nodes = []
            
            # Try several path variations
            path_variations = [
                file_path,
                file_path.replace("django/", ""),  # Remove django/ prefix if present
                os.path.basename(file_path),       # Just the file name
            ]
            
            # Also try with normalized paths
            norm_variations = set([PathResolver.normalize_path(p) for p in path_variations])
            
            # Combine all unique variations
            path_variations = list(set(path_variations) | norm_variations)
            
            logger.debug(f"Trying path variations: {path_variations}")
            
            # Try each variation
            for node_id, node in self.nodes_map.items():
                node_file_path = node.get("file_path", "")
                if not node_file_path:
                    continue
                    
                node_name_match = node.get("name") == node_name
                if not node_name_match:
                    continue
                
                # Normalize the node's file path
                norm_node_path = PathResolver.normalize_path(node_file_path)
                
                # Check if any variation matches
                for path_var in path_variations:
                    if (node_file_path == path_var or 
                        norm_node_path == path_var or
                        node_file_path.endswith(path_var) or
                        norm_node_path.endswith(path_var)):
                        matching_nodes.append(node)
                        logger.debug(f"Found matching node: {node_id} with file_path={node_file_path}")
                        break
            
            if matching_nodes:
                logger.debug(f"Found {len(matching_nodes)} nodes with name='{node_name}' in paths matching {file_path}")
                return matching_nodes
            
            # No matches found by qualified name
            logger.warning(f"No nodes found matching file_path='{file_path}' and name='{node_name}'")
            
            # Continue with regular file path matching on just the file path component
            is_file_path = True
            target = file_path
        
        if is_file_path:
            # Target is a file path
            # Normalize for consistent matching
            norm_target = PathResolver.normalize_path(target)
            target_basename = os.path.basename(norm_target)
            
            # Try different matching strategies
            matching_nodes = []
            
            # 1. Try exact path match first
            if norm_target in self.file_nodes_map:
                node_ids = self.file_nodes_map[norm_target]
                matching_nodes.extend([self.nodes_map[node_id] for node_id in node_ids if node_id in self.nodes_map])
            
            # 2. Try suffix match (more lenient)
            if not matching_nodes:
                for path in self.file_nodes_map.keys():
                    if path.endswith(norm_target) or norm_target.endswith(path):
                        node_ids = self.file_nodes_map[path]
                        matching_nodes.extend([self.nodes_map[node_id] for node_id in node_ids 
                                              if node_id in self.nodes_map])
            
            # 3. Try basename match (most lenient)
            if not matching_nodes:
                for path in self.file_nodes_map.keys():
                    if path.endswith('/' + target_basename) or os.path.basename(path) == target_basename:
                        node_ids = self.file_nodes_map[path]
                        matching_nodes.extend([self.nodes_map[node_id] for node_id in node_ids 
                                              if node_id in self.nodes_map])
            
            # 4. Special case handling for django paths
            if not matching_nodes and 'django/' in target:
                stripped_target = target.replace('django/', '')
                norm_stripped = PathResolver.normalize_path(stripped_target)
                
                for path in self.file_nodes_map.keys():
                    if path.endswith(norm_stripped) or norm_stripped.endswith(path):
                        node_ids = self.file_nodes_map[path]
                        matching_nodes.extend([self.nodes_map[node_id] for node_id in node_ids 
                                              if node_id in self.nodes_map])
            
            if matching_nodes:
                logger.debug(f"Found {len(matching_nodes)} nodes for file path: {target}")
            
            return matching_nodes
        else:
            # Target is a node name
            # Try direct node ID match
            if target in self.nodes_map:
                return [self.nodes_map[target]]
            
            # Try name match (could be multiple with same name)
            matching_nodes = []
            for node_id, node in self.nodes_map.items():
                if node.get("name") == target:
                    matching_nodes.append(node)
            
            if matching_nodes:
                logger.debug(f"Found {len(matching_nodes)} nodes with name: {target}")
                return matching_nodes
            
            return []
    
    def _prioritize_nodes(self, target_nodes: List[Dict[str, Any]], 
                         critical_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize target nodes based on critical path ranking.
        
        Args:
            target_nodes: List of target node dictionaries
            critical_nodes: List of critical node dictionaries
            
        Returns:
            Prioritized list of node dictionaries
        """
        if not critical_nodes:
            # No critical path data, sort by coverage
            return sorted(target_nodes, 
                         key=lambda x: x.get("properties", {}).get("coverage", 100),
                         reverse=False)
        
        # Build critical node lookup map (node_id -> rank)
        critical_map = {}
        for node in critical_nodes:
            node_id = node.get("node_id")
            rank = node.get("rank", float('inf'))
            
            if node_id:
                critical_map[node_id] = rank
                
                # Add members of SCC nodes
                if node.get("is_scc", False):
                    members = node.get("members", [])
                    for member_id in members:
                        critical_map[member_id] = rank
        
        # Assign priority score to each target node
        for node in target_nodes:
            node_id = node.get("id")
            if node_id in critical_map:
                # Node is in critical path, use its rank
                node["priority"] = critical_map[node_id]
            else:
                # Node is not in critical path, use lower priority
                node["priority"] = float('inf')
        
        # Sort by priority (rank) first, then by coverage (lower is higher priority)
        return sorted(target_nodes, 
                     key=lambda x: (x.get("priority", float('inf')), 
                                   x.get("properties", {}).get("coverage", 100)))
    
    def _generate_suggestions(self, nodes: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
        """Generate test suggestions for the given nodes.
        
        Args:
            nodes: List of node dictionaries
            k: Maximum number of suggestions to generate
            
        Returns:
            List of test suggestions
        """
        suggestions = []
        
        # Process top-k nodes
        for node in nodes[:k]:
            # Try to generate heuristic suggestions first
            heuristic_suggestions = self._generate_heuristic_suggestions(node)
            
            if heuristic_suggestions:
                suggestions.extend(heuristic_suggestions)
            elif self.llm_enabled:
                # Fall back to LLM if heuristics failed
                llm_suggestions = self._generate_llm_suggestions(node)
                suggestions.extend(llm_suggestions)
            
            # Limit to k suggestions
            if len(suggestions) >= k:
                return suggestions[:k]
        
        return suggestions
    
    def _generate_heuristic_suggestions(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test suggestions using heuristic rules based on AST analysis.
        
        Args:
            node: Node dictionary
            
        Returns:
            List of test suggestions
        """
        suggestions = []
        
        try:
            # Get node information
            node_id = node.get("id", "")
            name = node.get("name", "")
            file_path = node.get("file_path", "")
            
            if not name or not file_path:
                logger.warning(f"Node missing name or file path: {node_id}")
                return []
            
            # Get current directory and repo root
            cwd = Path.cwd()
            repo_root = PathResolver.repo_root()
            logger.debug(f"Current directory: {cwd}")
            logger.debug(f"Repository root: {repo_root}")
            logger.debug(f"Looking for source file: {file_path}")
            
            # Use the improved path resolution
            found_path = self._resolve_source_file(file_path)
            
            if not found_path:
                logger.warning(f"Source file not found for: {file_path}")
                return []
            
            # Read the file content
            try:
                with open(found_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.debug(f"Found source file at: {found_path}")
            except Exception as e:
                logger.debug(f"Error reading {found_path}: {e}")
                return []
            
            if not content:
                logger.warning(f"Source file not found for: {file_path}")
                logger.debug(f"Tried paths: {[str(p) for p in source_paths]}")
                return []
                
            # Parse the file and extract the function/method
            logger.debug(f"Parsing file: {found_path}")
            tree = ast.parse(content)
            
            # Find the node's AST
            node_ast = self._find_node_ast(tree, name)
            if not node_ast:
                logger.warning(f"Could not find AST for node: {name} in {file_path}")
                logger.debug(f"Available top-level entities: {[n.name for n in ast.iter_child_nodes(tree) if hasattr(n, 'name')]}")
                return []
                
            # Extract function parameters and type hints
            params, type_hints = self._extract_params_and_hints(node_ast)
            
            # Generate test cases based on parameter types
            test_cases = self._generate_test_cases(name, params, type_hints)
            
            # Convert test cases to suggestions
            for i, test_case in enumerate(test_cases):
                test_name = f"test_{name}_{test_case['scenario']}"
                test_file = Path(file_path).name
                
                suggestion = {
                    "test_name": f"{test_file}::{test_name}",
                    "target_node": f"{file_path}::{name}",
                    "estimated_coverage_gain": self._estimate_coverage_gain(node),
                    "skeleton": self._generate_pytest_skeleton(test_name, test_case),
                    "description": test_case["description"],
                    "scenario": test_case['scenario'],
                    "llm": False
                }
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Error generating heuristic suggestions: {e}")
            logger.debug(f"Error details: {traceback.format_exc()}")
            return []
    
    def _find_node_ast(self, tree: ast.AST, name: str) -> Optional[ast.AST]:
        """Find the AST node for a given function or method.
        
        Args:
            tree: AST of the file
            name: Name of the function or method
            
        Returns:
            AST node if found, None otherwise
        """
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == name:
                    return node
            elif isinstance(node, ast.ClassDef):
                for subnode in node.body:
                    if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if subnode.name == name:
                            return subnode
        return None
    
    def _resolve_source_file(self, file_path: str) -> Optional[Path]:
        """Robust file resolution with multiple fallback strategies."""
        if not file_path:
            return None
            
        resolver = PathResolver()
        
        # Strategy 1: Direct path resolution
        try:
            resolved_path = resolver.to_absolute(file_path)
            if resolved_path.exists():
                return resolved_path
        except Exception:
            pass
        
        # Strategy 2: Repository-relative paths
        try:
            repo_root = resolver.repo_root()
            repo_relative = repo_root / file_path
            if repo_relative.exists():
                return repo_relative
        except Exception:
            pass
        
        # Strategy 3: Common source directory patterns
        try:
            repo_root = resolver.repo_root()
            for pattern in ['src/', 'lib/', 'app/', 'testindex/', 'django/', '']:
                if pattern and file_path.startswith(pattern):
                    candidate = repo_root / file_path
                else:
                    candidate = repo_root / pattern / file_path.replace(pattern, '') if pattern else repo_root / file_path
                    
                if candidate.exists():
                    return candidate
        except Exception:
            pass
        
        # Strategy 4: Basename matching
        try:
            repo_root = resolver.repo_root()
            basename = os.path.basename(file_path)
            for pattern in ['src/', 'lib/', 'app/', 'testindex/', 'django/', '']:
                candidate = repo_root / pattern / basename
                if candidate.exists():
                    return candidate
        except Exception:
            pass
        
        logger.warning(f"Could not resolve source file: {file_path}")
        return None
    
    def _find_source_file(self, file_path: str) -> Optional[Path]:
        """Legacy method for backward compatibility."""
        return self._resolve_source_file(file_path)
        
    def _extract_dependencies(self, node: Dict[str, Any]) -> List[str]:
        """Extract dependencies for a node.
        
        Args:
            node: Node dictionary
            
        Returns:
            List of dependency names
        """
        dependencies = []
        
        # Check for explicit dependencies in node data
        if "dependencies" in node:
            return node["dependencies"]
            
        # Check for edges in the graph
        node_id = node.get("id")
        if not node_id:
            return dependencies
            
        # This would require loading edges data
        # For now, return empty list as this is just for display
        return dependencies
        
    def _extract_params_from_node(self, node: Dict[str, Any], source_code: str) -> Tuple[List[str], Dict[str, str]]:
        """Extract parameters and type hints from a node.
        
        Args:
            node: Node dictionary
            source_code: Source code of the file
            
        Returns:
            Tuple of (parameter names, type hints)
        """
        params = []
        type_hints = {}
        
        # Check if we have source code to parse
        if not source_code:
            return params, type_hints
            
        try:
            # Parse source code
            tree = ast.parse(source_code)
            
            # Find node's AST
            node_name = node.get("name", "")
            node_ast = self._find_node_ast(tree, node_name)
            
            if node_ast:
                # Extract parameters from AST
                params, type_hints = self._extract_params_and_hints(node_ast)
        except Exception as e:
            logger.warning(f"Failed to extract parameters: {e}")
            
        return params, type_hints
    
    def _extract_params_and_hints(self, node_ast: ast.AST) -> Tuple[List[str], Dict[str, str]]:
        """Extract function parameters and type hints.
        
        Args:
            node_ast: AST node for the function or method
            
        Returns:
            Tuple of (parameter names, type hints)
        """
        if not isinstance(node_ast, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return [], {}
            
        # Extract parameter names
        params = []
        for arg in node_ast.args.args:
            params.append(arg.arg)
            
        # Extract type hints
        type_hints = {}
        for arg in node_ast.args.args:
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    type_hints[arg.arg] = arg.annotation.id
                elif isinstance(arg.annotation, ast.Subscript):
                    if isinstance(arg.annotation.value, ast.Name):
                        type_hints[arg.arg] = f"{arg.annotation.value.id}[...]"
                    else:
                        type_hints[arg.arg] = "complex"
                elif isinstance(arg.annotation, ast.Attribute):
                    type_hints[arg.arg] = arg.annotation.attr
                else:
                    type_hints[arg.arg] = "unknown"
            
        return params, type_hints
    
    def _generate_boundary_cases(self, param_name: str, param_type: str, type_hint: str = None) -> List[Dict]:
        """Generate comprehensive boundary test cases."""
        cases = []
        
        # Type-specific boundary cases
        if param_type in ['int', 'float'] or 'int' in str(type_hint) or 'float' in str(type_hint):
            cases.extend([
                {"scenario": f"{param_name}_zero", "value": "0", "expected": "valid"},
                {"scenario": f"{param_name}_negative", "value": "-1", "expected": "error"},
                {"scenario": f"{param_name}_large", "value": "999999", "expected": "valid"},
                {"scenario": f"{param_name}_max_int", "value": "2147483647", "expected": "valid"},
            ])
        elif param_type == 'str' or 'str' in str(type_hint):
            cases.extend([
                {"scenario": f"{param_name}_empty", "value": '""', "expected": "error"},
                {"scenario": f"{param_name}_long", "value": '"x" * 1000', "expected": "valid"},
                {"scenario": f"{param_name}_none", "value": "None", "expected": "error"},
                {"scenario": f"{param_name}_unicode", "value": '"𝒽𝑒𝓁𝓁𝑜"', "expected": "valid"},
                {"scenario": f"{param_name}_newlines", "value": '"line1\\nline2"', "expected": "valid"},
            ])
        elif param_type in ['list', 'tuple'] or any(x in str(type_hint) for x in ['List', 'Tuple']):
            cases.extend([
                {"scenario": f"{param_name}_empty", "value": "[]", "expected": "valid"},
                {"scenario": f"{param_name}_none", "value": "None", "expected": "error"},
                {"scenario": f"{param_name}_single", "value": "[1]", "expected": "valid"},
                {"scenario": f"{param_name}_large", "value": "list(range(1000))", "expected": "valid"},
            ])
        elif param_type in ['dict'] or 'Dict' in str(type_hint):
            cases.extend([
                {"scenario": f"{param_name}_empty", "value": "{}", "expected": "valid"},
                {"scenario": f"{param_name}_none", "value": "None", "expected": "error"},
                {"scenario": f"{param_name}_nested", "value": '{"key": {"nested": "value"}}', "expected": "valid"},
            ])
        elif param_type == 'bool' or 'bool' in str(type_hint):
            cases.extend([
                {"scenario": f"{param_name}_true", "value": "True", "expected": "valid"},
                {"scenario": f"{param_name}_false", "value": "False", "expected": "valid"},
            ])
        else:
            # Generic test cases for unknown types
            cases.extend([
                {"scenario": f"{param_name}_none", "value": "None", "expected": "error"},
                {"scenario": f"{param_name}_valid", "value": "test_value", "expected": "valid"},
            ])
        
        return cases

    def _generate_test_cases(self, func_name: str, params: List[str], 
                            type_hints: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate test cases based on parameter types.
        
        Args:
            func_name: Function name
            params: List of parameter names
            type_hints: Dictionary mapping parameter names to type hints
            
        Returns:
            List of test cases
        """
        test_cases = []
        
        # Skip self/cls parameters for methods
        if params and params[0] in ('self', 'cls'):
            params = params[1:]
            
        # If no parameters, generate simple test case
        if not params:
            test_cases.append({
                "scenario": "basic",
                "params": {},
                "expected": "expected_result",
                "description": f"Basic test for {func_name}"
            })
            return test_cases
        
        # Generate comprehensive boundary test cases
        for param in params:
            param_type = type_hints.get(param, "unknown")
            boundary_cases = self._generate_boundary_cases(param, param_type, param_type)
            
            for case in boundary_cases:
                test_cases.append({
                    "scenario": case["scenario"],
                    "params": {param: case["value"]},
                    "expected": case["expected"],
                    "description": f"Test {func_name} with boundary condition: {case['scenario']}"
                })
        
        # Generate happy path test case with valid inputs
        if params:
            happy_path_params = {}
            for param in params:
                param_type = type_hints.get(param, "unknown")
                if param_type in ['int', 'float'] or 'int' in str(param_type):
                    happy_path_params[param] = "10"
                elif param_type == 'str' or 'str' in str(param_type):
                    happy_path_params[param] = '"valid_string"'
                elif param_type in ['list'] or 'List' in str(param_type):
                    happy_path_params[param] = "[1, 2, 3]"
                elif param_type in ['dict'] or 'Dict' in str(param_type):
                    happy_path_params[param] = '{"key": "value"}'
                elif param_type == 'bool':
                    happy_path_params[param] = "True"
                else:
                    happy_path_params[param] = "test_value"
            
            test_cases.append({
                "scenario": "happy_path",
                "params": happy_path_params,
                "expected": "valid",
                "description": f"Happy path test for {func_name} with valid inputs"
            })
        
        return test_cases
    
    def _generate_pytest_skeleton(self, test_name: str, test_case: Dict[str, Any]) -> str:
        """Generate a pytest skeleton for a test case.
        
        Args:
            test_name: Name of the test
            test_case: Test case dictionary
            
        Returns:
            Pytest skeleton
        """
        # Format parameters
        params_str = ", ".join([f"{name}={value}" for name, value in test_case.get("params", {}).items()])
        
        # Generate skeleton
        return f"""def {test_name}():
    \"\"\"
    {test_case.get('description', 'Test case')}
    \"\"\"
    # Arrange
    {params_str}
    expected = {test_case.get('expected', 'None')}
    
    # Act
    result = # Call the function under test
    
    # Assert
    assert result == expected"""
    
    def _generate_llm_suggestions(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test suggestions using LLM.
        
        Args:
            node: Node dictionary
            
        Returns:
            List of test suggestions
        """
        # Only attempt if LLM is enabled
        if not self.llm_enabled:
            return []
            
        try:
            # Check if OpenAI client is available
            try:
                from testindex.llm.clients.openai_client import OpenAIClient
            except ImportError:
                logger.error("OpenAI client not available. Install with: pip install openai")
                return []
                
            # Get node information
            node_id = node.get("id", "")
            name = node.get("name", "")
            file_path = node.get("file_path", "")
            
            if not name or not file_path:
                logger.warning(f"Node missing name or file path: {node_id}")
                return []
                
            # Read the file
            full_path = PathResolver.to_absolute(file_path)
            if not full_path.exists():
                logger.warning(f"File not found: {full_path}")
                return []
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Initialize client
            client = OpenAIClient(model=self.model, budget=self.budget)
            
            # Generate prompt
            prompt = self._generate_llm_prompt(node, name, file_path, content)
            
            # Call LLM
            suggestions = client.generate_test_suggestions(prompt, name, file_path)
            
            # Add LLM attribution
            for suggestion in suggestions:
                suggestion["llm"] = True
                suggestion["model"] = self.model
                
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate LLM suggestions: {e}")
            return []
    
    def _generate_llm_prompt(self, node: Dict[str, Any], name: str, 
                           file_path: str, content: str) -> str:
        """Generate a prompt for the LLM.
        
        Args:
            node: Node dictionary
            name: Function name
            file_path: File path
            content: File content
            
        Returns:
            Prompt string
        """
        return f"""
You are a test expert. Your task is to generate pytest test cases for the function named '{name}' in the file '{file_path}'.

Here's the file content:
```python
{content}
```

Focus on the function '{name}' and generate up to 3 high-quality test cases.
For each test case, provide:
1. A descriptive test name
2. A brief explanation of what the test verifies
3. A complete pytest function implementation with arrange-act-assert pattern

Prioritize test cases that would:
- Test edge cases and boundary conditions
- Maximize code coverage
- Verify error handling
- Test important business logic paths

Return each test case as a JSON object with the following structure:
{{
  "test_name": "test_function_name_scenario",
  "description": "Brief description of what this test verifies",
  "skeleton": "def test_name():\\n    # Arrange\\n    ...\\n    # Act\\n    ...\\n    # Assert\\n    ..."
}}

Return a list of these test case objects. Skip any explanatory text or comments.
"""
    
    def _estimate_coverage_gain(self, node: Dict[str, Any]) -> float:
        """Estimate coverage gain from testing a node.
        
        Args:
            node: Node dictionary
            
        Returns:
            Estimated coverage gain
        """
        properties = node.get("properties", {})
        loc = properties.get("loc", 0)
        coverage_pct = properties.get("coverage", 0)
        
        # Calculate uncovered LOC
        uncovered_loc = loc * (1 - coverage_pct / 100)
        
        # Apply a discount factor for partial coverage
        return max(1, uncovered_loc)
    
    def _write_output(self, suggestions: List[Dict[str, Any]], output_file: Path) -> None:
        """Write suggestions to output file.
        
        Args:
            suggestions: List of suggestion dictionaries
            output_file: Path to output file
        """
        output = {
            "version": "K1",
            "suggestions": suggestions
        }
        
        try:
            # Ensure parent directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            
            logger.info(f"Test suggestions written to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write output: {str(e)}") 