"""
Diff Analyzer for TestIndex.

This module identifies implementation nodes and related tests impacted by changes
in a git diff, using the knowledge graph.
"""

import json
import os
import time
import networkx as nx
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.utils.git import GitManager, memoize_repo
from testindex.analysis.criticality_scorer import CriticalityScorer, CriticalityWeights

# Set up logger
logger = get_logger(__name__)


class DiffAnalyzerError(Exception):
    """Raised when there's an error during diff analysis."""
    pass


class DiffAnalyzer:
    """Analyzes git diffs to identify impacted nodes and related tests."""
    
    def __init__(self, depth: int = 1, criticality_weights: Optional[CriticalityWeights] = None):
        """Initialize the diff analyzer.
        
        Args:
            depth: Depth of call graph traversal (default: 1)
            criticality_weights: Custom criticality weights, uses defaults if None
        """
        self.depth = depth
        self.git_manager = GitManager()
        self.nodes_map = {}  # id -> node
        self.file_to_nodes = {}  # file_path -> list of node_ids
        self.graph = None
        self.criticality_scorer = CriticalityScorer(criticality_weights)
        self._all_nodes = []  # Cache for all nodes
        self._all_edges = []  # Cache for all edges
        
    def analyze(self, 
                since: str,
                until: str = "HEAD",
                nodes_file: Optional[Union[str, Path]] = None,
                edges_file: Optional[Union[str, Path]] = None,
                output_file: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """Analyze git diff to find impacted nodes and tests.
        
        Args:
            since: Git reference to compare from (e.g., "HEAD~1")
            until: Git reference to compare to (default: "HEAD")
            nodes_file: Path to the nodes.json file (optional)
            edges_file: Path to the edges.json file (optional)
            output_file: Path to write the diff.json file (optional)
            
        Returns:
            List of impacted nodes with related information
        """
        start_time = time.time()
        
        # Check if this is a git repository
        if not self.git_manager.is_git_repository():
            raise DiffAnalyzerError("Not a git repository")
        
        # Use default paths if not provided
        if nodes_file is None:
            nodes_file = PathResolver.nodes_file()
        if edges_file is None:
            edges_file = PathResolver.edges_file()
        if output_file is None:
            output_file = PathResolver.knowledge_graph_dir() / "diff.json"
            
        nodes_file = Path(nodes_file)
        edges_file = Path(edges_file)
        output_file = Path(output_file)
        
        logger.info(f"Analyzing diff from {since} to {until}")
        logger.info(f"Using nodes from {nodes_file} and edges from {edges_file}")
        logger.info(f"Output will be written to {output_file}")
        
        # Ensure required input files exist
        if not nodes_file.exists():
            raise DiffAnalyzerError(f"Nodes file not found: {nodes_file}")
        if not edges_file.exists():
            raise DiffAnalyzerError(f"Edges file not found: {edges_file}")
        
        # Get changed files from git
        changed_files = self.git_manager.get_changed_files(since, until)
        if not changed_files:
            logger.info("No files changed")
            return []
            
        logger.info(f"Found {len(changed_files)} changed files")
        
        # Load nodes and edges
        nodes, edges = self._load_data(nodes_file, edges_file)
        
        # Cache for criticality scoring
        self._all_nodes = nodes
        self._all_edges = edges
        
        # Build lookup maps
        self._build_lookup_maps(nodes)
        
        # Build call graph
        self.graph = self._build_call_graph(nodes, edges)
        
        # Find impacted implementation nodes
        impacted_nodes = self._find_impacted_nodes(changed_files)
        
        # Find related tests
        self._find_related_tests(impacted_nodes)
        
        # Write to output file
        self._write_output(impacted_nodes, output_file)
        
        # Calculate duration
        duration = time.time() - start_time
        logger.info(f"Diff analysis completed in {duration:.2f}s")
        logger.info(f"Found {len(impacted_nodes)} impacted nodes")
        
        return impacted_nodes

    def calculate_risk_score(self, impacted_nodes: List[Dict[str, Any]], use_criticality: bool = True) -> Dict[str, Any]:
        """Calculate risk scores for the change impact with optional criticality weighting.
        
        Args:
            impacted_nodes: List of impacted nodes from analyze()
            use_criticality: Whether to use criticality-weighted scoring
        
        Returns:
            Dict containing risk metrics and recommendations
        """
        if not impacted_nodes:
            return {"risk_level": "LOW", "score": 0.0, "reasons": [], "criticality_enabled": use_criticality}
        
        # Risk factors
        total_score = 0.0
        reasons = []
        node_count = len(impacted_nodes)
        
        if use_criticality and self._all_nodes and self._all_edges:
            # Enhanced criticality-based risk calculation
            try:
                # Factor 1: Weighted impact score (replaces simple node count)
                weighted_impact = self.criticality_scorer.calculate_weighted_impact_score(
                    impacted_nodes, self._all_nodes, self._all_edges
                )
                
                # Scale weighted impact to match traditional 0.4 max contribution
                impact_score = weighted_impact * 0.5
                total_score += impact_score
                
                if weighted_impact > 0.6:
                    reasons.append(f"High criticality impact: {node_count} nodes (weighted score: {weighted_impact:.3f})")
                elif weighted_impact > 0.3:
                    reasons.append(f"Medium criticality impact: {node_count} nodes (weighted score: {weighted_impact:.3f})")
                else:
                    reasons.append(f"Low criticality impact: {node_count} nodes (weighted score: {weighted_impact:.3f})")
                
                # Factor 2: Critical nodes (enhanced with actual criticality scores)
                criticality_scores = self.criticality_scorer.calculate_criticality_scores(
                    self._all_nodes, self._all_edges
                )
                
                highly_critical_nodes = [
                    n for n in impacted_nodes 
                    if criticality_scores.get(n.get('id'), 0.0) > 0.7
                ]
                
                if highly_critical_nodes:
                    critical_score = min(0.3, len(highly_critical_nodes) / node_count * 0.3)
                    total_score += critical_score
                    avg_criticality = sum(criticality_scores.get(n.get('id'), 0.0) for n in highly_critical_nodes) / len(highly_critical_nodes)
                    reasons.append(f"High-criticality nodes affected: {len(highly_critical_nodes)} nodes (avg criticality: {avg_criticality:.3f})")
                
                # Factor 3: Test coverage gaps (unchanged)
                uncovered_nodes = [n for n in impacted_nodes if not n.get("tests")]
                if uncovered_nodes:
                    coverage_risk = len(uncovered_nodes) / node_count
                    total_score += coverage_risk * 0.3
                    reasons.append(f"Test coverage gap: {len(uncovered_nodes)} nodes without tests")
                
            except Exception as e:
                logger.warning(f"Failed to calculate criticality-based risk, falling back to legacy: {e}")
                # Fall back to legacy calculation
                return self._calculate_legacy_risk_score(impacted_nodes)
                
        else:
            # Legacy risk calculation
            return self._calculate_legacy_risk_score(impacted_nodes)
        
        # Determine risk level
        if total_score >= 0.7:
            risk_level = "HIGH"
        elif total_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "score": round(total_score, 2),
            "reasons": reasons,
            "node_count": node_count,
            "critical_nodes": len(highly_critical_nodes) if use_criticality else len([n for n in impacted_nodes if n.get("calls_in", 0) > 5]),
            "uncovered_nodes": len([n for n in impacted_nodes if not n.get("tests")]),
            "criticality_enabled": use_criticality,
            "weighted_impact_score": weighted_impact if use_criticality else None
        }
    
    def _calculate_legacy_risk_score(self, impacted_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk scores using the original algorithm.
        
        Args:
            impacted_nodes: List of impacted nodes from analyze()
        
        Returns:
            Dict containing risk metrics and recommendations
        """
        # Original risk calculation logic
        total_score = 0.0
        reasons = []
        node_count = len(impacted_nodes)
        
        # Factor 1: Number of impacted nodes
        if node_count > 20:
            total_score += 0.4
            reasons.append(f"High impact scope: {node_count} nodes affected")
        elif node_count > 10:
            total_score += 0.2
            reasons.append(f"Medium impact scope: {node_count} nodes affected")
        
        # Factor 2: Critical path involvement
        critical_nodes = [n for n in impacted_nodes if n.get("calls_in", 0) > 5]
        if critical_nodes:
            total_score += 0.3
            reasons.append(f"Critical nodes affected: {len(critical_nodes)} high-connectivity nodes")
        
        # Factor 3: Test coverage gaps
        uncovered_nodes = [n for n in impacted_nodes if not n.get("tests")]
        if uncovered_nodes:
            coverage_risk = len(uncovered_nodes) / node_count
            total_score += coverage_risk * 0.3
            reasons.append(f"Test coverage gap: {len(uncovered_nodes)} nodes without tests")
        
        # Determine risk level
        if total_score >= 0.7:
            risk_level = "HIGH"
        elif total_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "score": round(total_score, 2),
            "reasons": reasons,
            "node_count": node_count,
            "critical_nodes": len(critical_nodes),
            "uncovered_nodes": len(uncovered_nodes),
            "criticality_enabled": False
        }

    def find_test_execution_plan(self, impacted_nodes: List[Dict[str, Any]], use_criticality: bool = True) -> List[str]:
        """Generate optimal test execution plan for impacted changes with criticality ranking.
        
        Args:
            impacted_nodes: List of impacted nodes from analyze()
            use_criticality: Whether to use criticality-based test prioritization
        
        Returns:
            List of test files ordered by priority
        """
        # Collect all related tests
        all_tests = set()
        test_priorities = {}
        
        if use_criticality and self._all_nodes and self._all_edges:
            try:
                # Get criticality scores for enhanced prioritization
                criticality_scores = self.criticality_scorer.calculate_criticality_scores(
                    self._all_nodes, self._all_edges
                )
                
                for node in impacted_nodes:
                    node_tests = node.get("tests", [])
                    all_tests.update(node_tests)
                    
                    # Use criticality score as priority
                    node_id = node.get('id')
                    criticality = criticality_scores.get(node_id, 0.0)
                    
                    # Boost priority for nodes with higher criticality
                    priority = criticality * 100  # Scale to reasonable range
                    
                    for test in node_tests:
                        test_priorities[test] = max(test_priorities.get(test, 0), priority)
                        
            except Exception as e:
                logger.warning(f"Failed to use criticality for test prioritization, falling back to legacy: {e}")
                return self._find_legacy_test_execution_plan(impacted_nodes)
                
        else:
            # Legacy test prioritization
            return self._find_legacy_test_execution_plan(impacted_nodes)
        
        # Sort tests by priority (descending)
        sorted_tests = sorted(all_tests, key=lambda t: test_priorities.get(t, 0), reverse=True)
        
        return sorted_tests
    
    def _find_legacy_test_execution_plan(self, impacted_nodes: List[Dict[str, Any]]) -> List[str]:
        """Generate test execution plan using legacy connectivity-based prioritization.
        
        Args:
            impacted_nodes: List of impacted nodes from analyze()
        
        Returns:
            List of test files ordered by priority
        """
        all_tests = set()
        test_priorities = {}
        
        for node in impacted_nodes:
            node_tests = node.get("tests", [])
            all_tests.update(node_tests)
            
            # Prioritize tests for high-connectivity nodes (legacy method)
            priority = node.get("calls_in", 0) + node.get("calls_out", 0)
            for test in node_tests:
                test_priorities[test] = max(test_priorities.get(test, 0), priority)
        
        # Sort tests by priority (descending)
        sorted_tests = sorted(all_tests, key=lambda t: test_priorities.get(t, 0), reverse=True)
        
        return sorted_tests
    
    @memoize_repo
    def _load_data(self, nodes_file: Path, edges_file: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load nodes and edges from JSON files.
        
        Args:
            nodes_file: Path to nodes.json
            edges_file: Path to edges.json
            
        Returns:
            Tuple of (nodes, edges) lists
        """
        try:
            with open(nodes_file, 'r') as f:
                nodes_data = json.load(f)
            
            # Handle both direct list and object with "nodes" field formats
            if isinstance(nodes_data, dict) and "nodes" in nodes_data:
                nodes = nodes_data["nodes"]
            else:
                nodes = nodes_data
                
            logger.info(f"Loaded {len(nodes)} nodes from {nodes_file}")
        except Exception as e:
            raise DiffAnalyzerError(f"Failed to load nodes: {str(e)}")
            
        try:
            with open(edges_file, 'r') as f:
                edges_data = json.load(f)
                
            # Handle both direct list and object with "edges" field formats
            if isinstance(edges_data, dict) and "edges" in edges_data:
                edges = edges_data["edges"]
            else:
                edges = edges_data
                
            logger.info(f"Loaded {len(edges)} edges from {edges_file}")
        except Exception as e:
            raise DiffAnalyzerError(f"Failed to load edges: {str(e)}")
            
        return nodes, edges
    
    def _build_lookup_maps(self, nodes: List[Dict[str, Any]]) -> None:
        """Build lookup maps for efficient node access.
        
        Args:
            nodes: List of node dictionaries
        """
        for node in nodes:
            node_id = node.get("id")
            if node_id:
                self.nodes_map[node_id] = node
                
                # Build file path to nodes map
                file_path = node.get("file_path")
                if file_path:
                    # Normalize file path for consistent comparison
                    norm_path = PathResolver.normalize_path(file_path)
                    if norm_path not in self.file_to_nodes:
                        self.file_to_nodes[norm_path] = []
                    self.file_to_nodes[norm_path].append(node_id)
    
    def _build_call_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build a call graph from nodes and edges.
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
            
        Returns:
            NetworkX DiGraph representing the call graph
        """
        G = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            node_id = node.get("id")
            if node_id:
                G.add_node(node_id, **node)
        
        # Add edges (only CALLS type)
        call_edges = [e for e in edges if isinstance(e, dict) and e.get("type") == "CALLS"]
        for edge in call_edges:
            # Handle both source/target and src/dst field naming conventions
            source = edge.get("source") or edge.get("src")
            target = edge.get("target") or edge.get("dst")
            if source and target and G.has_node(source) and G.has_node(target):
                G.add_edge(source, target)
        
        logger.info(f"Built call graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        return G
    
    def _find_impacted_nodes(self, changed_files: List[Path]) -> List[Dict[str, Any]]:
        """Find implementation nodes impacted by changed files.
        
        Args:
            changed_files: List of changed file paths
            
        Returns:
            List of impacted node dictionaries
        """
        impacted_node_ids = set()
        
        # First pass: direct file changes
        for file_path in changed_files:
            norm_path = PathResolver.normalize_path(file_path)
            
            # Try different matching strategies if direct match fails
            matched = False
            for path_key in self.file_to_nodes.keys():
                if (norm_path == path_key or 
                    norm_path.endswith(path_key) or 
                    path_key.endswith(norm_path)):
                    
                    # Add all nodes in this file
                    impacted_node_ids.update(self.file_to_nodes[path_key])
                    matched = True
            
            if not matched:
                logger.debug(f"No nodes found for file {file_path}")
        
        # Second pass: expand to callees based on depth
        if self.depth > 0:
            expanded_nodes = set(impacted_node_ids)
            current_depth = 0
            
            while current_depth < self.depth:
                next_level = set()
                for node_id in expanded_nodes:
                    # Get immediate successors (nodes that this node calls)
                    if node_id in self.graph:
                        successors = self.graph.successors(node_id)
                        next_level.update(successors)
                
                # Add new nodes and continue to next depth
                new_nodes = next_level - expanded_nodes
                expanded_nodes.update(new_nodes)
                current_depth += 1
                
                logger.debug(f"Depth {current_depth}: Added {len(new_nodes)} nodes")
                
                # Stop early if no new nodes were added
                if not new_nodes:
                    break
            
            impacted_node_ids = expanded_nodes
        
        # Convert IDs to full node dictionaries
        impacted_nodes = []
        for node_id in impacted_node_ids:
            if node_id in self.nodes_map:
                node = self.nodes_map[node_id]
                
                # Only include implementation nodes (not tests)
                if node.get("type") == "Implementation":
                    # Initialize the result structure
                    impacted_node = {
                        "id": node_id,
                        "file": node.get("file_path", ""),
                        "change": self._get_change_type(node.get("file_path", ""), changed_files),
                        "calls_in": 0,
                        "calls_out": 0,
                        "tests": []
                    }
                    
                    # Count incoming and outgoing calls
                    if self.graph.has_node(node_id):
                        impacted_node["calls_in"] = self.graph.in_degree(node_id)
                        impacted_node["calls_out"] = self.graph.out_degree(node_id)
                    
                    impacted_nodes.append(impacted_node)
        
        return impacted_nodes
    
    def _get_change_type(self, file_path: str, changed_files: List[Path]) -> str:
        """Determine the type of change for a file.
        
        Args:
            file_path: The file path to check
            changed_files: List of changed file paths
            
        Returns:
            str: Change type ('added', 'modified', or 'unknown')
        """
        if not file_path:
            return "unknown"
        
        norm_path = PathResolver.normalize_path(file_path)
        
        for changed_file in changed_files:
            changed_norm = PathResolver.normalize_path(str(changed_file))
            
            # Direct match or path endings match
            if (norm_path == changed_norm or 
                norm_path.endswith(changed_norm) or 
                changed_norm.endswith(norm_path)):
                
                # Check if it's a new file
                if not Path(file_path).exists():
                    return "added"
                return "modified"
                
        return "unknown"
    
    def _find_related_tests(self, impacted_nodes: List[Dict[str, Any]]) -> None:
        """Find tests related to impacted implementation nodes.
        
        Args:
            impacted_nodes: List of impacted node dictionaries
            
        This method modifies the impacted_nodes list in-place.
        """
        for node in impacted_nodes:
            node_id = node["id"]
            
            # Find all tests that call this node
            if self.graph.has_node(node_id):
                # Get test nodes that call this implementation
                test_nodes = []
                
                # First look for direct callers that are tests
                for caller_id in self.graph.predecessors(node_id):
                    caller = self.nodes_map.get(caller_id, {})
                    if caller.get("type") == "Test" or "tests/" in caller.get("file_path", ""):
                        test_nodes.append(caller)
                
                # Extract test file paths
                test_files = set()
                for test_node in test_nodes:
                    test_file = test_node.get("file_path")
                    if test_file:
                        test_files.add(test_file)
                
                # Add test files to node
                node["tests"] = sorted(list(test_files))
    
    def _write_output(self, impacted_nodes: List[Dict[str, Any]], output_file: Path) -> None:
        """Write impacted nodes to a JSON file.
        
        Args:
            impacted_nodes: List of impacted node dictionaries
            output_file: Path to write to
        """
        try:
            # Create parent directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Build output structure
            output = {
                "version": "0.3.0",
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "nodes": impacted_nodes
            }
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
                
            logger.info(f"Wrote {len(impacted_nodes)} impacted nodes to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write output: {e}")
            raise DiffAnalyzerError(f"Failed to write output: {str(e)}") 