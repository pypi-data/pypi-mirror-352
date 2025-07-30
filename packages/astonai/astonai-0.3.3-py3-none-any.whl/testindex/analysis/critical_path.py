"""
Critical Path Analyzer for TestIndex.

This module identifies critical implementation nodes in the knowledge graph
whose failure would maximally reduce overall test coverage.
"""

import json
import os
import time
import networkx as nx
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver

# Set up logger
logger = get_logger(__name__)


class CriticalPathError(Exception):
    """Raised when there's an error during critical path analysis."""
    pass


class CriticalPathAnalyzer:
    """Analyzes the knowledge graph to identify critical implementation nodes."""
    
    def __init__(self, weight_func: str = "loc"):
        """Initialize the critical path analyzer.
        
        Args:
            weight_func: Weight function to use (loc, calls, churn)
        """
        self.weight_func = weight_func
        self.nodes_map = {}  # id -> node
        self.dag = None
        
    def analyze(self, 
                nodes_file: Optional[Union[str, Path]] = None,
                edges_file: Optional[Union[str, Path]] = None,
                output_file: Optional[Union[str, Path]] = None,
                n: int = 50) -> List[Dict[str, Any]]:
        """Analyze the knowledge graph to find critical nodes.
        
        Args:
            nodes_file: Path to the nodes.json file (optional)
            edges_file: Path to the edges.json file (optional)
            output_file: Path to write the critical_path.json file (optional)
            n: Number of nodes to return (default 50)
            
        Returns:
            List of critical nodes with risk scores
        """
        start_time = time.time()
        
        # Use default paths if not provided
        if nodes_file is None:
            nodes_file = PathResolver.nodes_file()
        if edges_file is None:
            edges_file = PathResolver.edges_file()
        if output_file is None:
            output_file = PathResolver.knowledge_graph_dir() / "critical_path.json"
            
        nodes_file = Path(nodes_file)
        edges_file = Path(edges_file)
        output_file = Path(output_file)
        
        logger.info(f"Analyzing critical path from {nodes_file} and {edges_file}")
        logger.info(f"Output will be written to {output_file}")
        
        # Ensure required input files exist
        if not nodes_file.exists():
            raise CriticalPathError(f"Nodes file not found: {nodes_file}")
        if not edges_file.exists():
            raise CriticalPathError(f"Edges file not found: {edges_file}")
        
        # Load nodes and edges
        nodes, edges = self._load_data(nodes_file, edges_file)
        
        # Build lookup map for efficient node access
        self._build_nodes_map(nodes)
        
        # Handle cycles and build weighted DAG
        self.dag = self._handle_cycles(nodes, edges)
        self.dag = self._build_weighted_dag(self.dag, self.weight_func)
        
        # Calculate longest path scores
        scores = self._longest_path_scores(self.dag)
        
        # Rank critical nodes
        ranked_nodes = self._rank_critical_nodes(self.dag, scores, n)
        
        # Write to output file
        self._write_output(ranked_nodes, output_file)
        
        # Calculate duration
        duration = time.time() - start_time
        logger.info(f"Critical path analysis completed in {duration:.2f}s")
        logger.info(f"Found {len(ranked_nodes)} critical nodes")
        
        return ranked_nodes
    
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
            raise CriticalPathError(f"Failed to load nodes: {str(e)}")
            
        try:
            with open(edges_file, 'r') as f:
                edges_data = json.load(f)
                
            # Handle both direct list and object with "edges" field formats
            if isinstance(edges_data, dict) and "edges" in edges_data:
                edges = edges_data["edges"]
            else:
                edges = edges_data
                
            logger.info(f"Loaded {len(edges)} edges from {edges_file}")
            
            # Check for suspiciously low edge count (potential data issue)
            EDGE_COUNT_WARNING_THRESHOLD = 10
            if len(edges) < EDGE_COUNT_WARNING_THRESHOLD:
                logger.warning(f"Suspiciously low edge count detected: {len(edges)} edges")
                logger.warning("This may indicate an issue with edge extraction or field naming in edges.json")
                logger.warning("Check that edges contain 'src'/'dst' or 'source'/'target' fields and have 'type' field set")
                
                # Check the first few edges if available to give more context
                if edges:
                    sample_edge = edges[0]
                    logger.warning(f"Sample edge fields: {', '.join(sample_edge.keys())}")
                    if len(edges) > 1:
                        logger.warning(f"Number of CALLS edges: {sum(1 for e in edges if e.get('type') == 'CALLS')}")
                        logger.warning(f"Number of IMPORTS edges: {sum(1 for e in edges if e.get('type') == 'IMPORTS')}")
        except Exception as e:
            raise CriticalPathError(f"Failed to load edges: {str(e)}")
            
        return nodes, edges
    
    def _build_nodes_map(self, nodes: List[Dict[str, Any]]) -> None:
        """Build a lookup map for nodes by ID.
        
        Args:
            nodes: List of node dictionaries
        """
        for node in nodes:
            node_id = node.get("id")
            if node_id:
                self.nodes_map[node_id] = node
    
    def _handle_cycles(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> nx.DiGraph:
        """Handle cycles in the graph by collapsing strongly connected components.
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
            
        Returns:
            NetworkX DiGraph with cycles handled
        """
        # Create initial graph
        G = nx.DiGraph()
        
        # Add nodes (only implementation nodes, excluding test files)
        impl_nodes = [
            n for n in nodes 
            if isinstance(n, dict) and n.get("type") == "Implementation" 
            and "tests/" not in n.get("file_path", "")
        ]
        for node in impl_nodes:
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
        
        # Check if graph is already acyclic
        if nx.is_directed_acyclic_graph(G):
            logger.info("No cycles found in the call graph")
            return G
            
        # Find strongly connected components
        components = list(nx.strongly_connected_components(G))
        cycles = [comp for comp in components if len(comp) > 1]
        
        if not cycles:
            logger.info("No cycles found in the call graph")
            return G
            
        # Log cycle information
        cycle_count = len(cycles)
        total_nodes_in_cycles = sum(len(c) for c in cycles)
        logger.info(f"Found {cycle_count} cycles with {total_nodes_in_cycles} nodes in the call graph")
        
        # Collapse each cycle into a single node
        G_collapsed = nx.DiGraph()
        
        # Map from original nodes to their component (or themselves if not in a cycle)
        component_map = {}
        for i, component in enumerate(components):
            component_id = f"component_{i}" if len(component) > 1 else list(component)[0]
            for node in component:
                component_map[node] = component_id
        
        # Add nodes to the collapsed graph
        for component in components:
            if len(component) > 1:
                # This is a cycle - collapse into a single node
                component_id = component_map[list(component)[0]]
                
                # Combine properties of all nodes in the cycle
                combined_props = {"type": "Implementation", "cycle": True, "cycle_size": len(component)}
                nodes_in_cycle = []
                for node in component:
                    nodes_in_cycle.append(node)
                    node_data = G.nodes[node]
                    if isinstance(node_data, dict):
                        for k, v in node_data.items():
                            if k not in combined_props:
                                combined_props[k] = v
                combined_props["nodes_in_cycle"] = nodes_in_cycle
                
                G_collapsed.add_node(component_id, **combined_props)
            else:
                # Single node - just add it as is
                node = list(component)[0]
                G_collapsed.add_node(node, **G.nodes[node])
        
        # Add edges between components
        for u, v in G.edges():
            u_comp = component_map[u]
            v_comp = component_map[v]
            if u_comp != v_comp:  # Skip self-loops
                G_collapsed.add_edge(u_comp, v_comp)
        
        # Verify the collapsed graph is acyclic
        if not nx.is_directed_acyclic_graph(G_collapsed):
            logger.warning("Collapsing cycles did not result in an acyclic graph. Some cycles may remain.")
        else:
            logger.info("Successfully collapsed cycles to create an acyclic graph")
            
        return G_collapsed
    
    def _build_weighted_dag(self, G: nx.DiGraph, weight_func: str) -> nx.DiGraph:
        """Build a weighted DAG with node weights based on the specified function.
        
        Args:
            G: NetworkX DiGraph
            weight_func: Weight function to use (loc, calls, churn)
            
        Returns:
            Weighted NetworkX DiGraph
        """
        for node_id in G.nodes:
            # Add defensive check to make sure G.nodes[node_id] returns a dictionary not a string
            node_data = G.nodes[node_id]
            if not isinstance(node_data, dict):
                logger.warning(f"Skipping weight calculation for non-dictionary node data for node_id {node_id}")
                G.nodes[node_id] = {"weight": 1}
                continue
                
            if node_data.get("is_scc", False):
                # Handle super-node (SCC)
                members = node_data.get("members", [])
                weight = 0
                for member_id in members:
                    if member_id in self.nodes_map:
                        member_node = self.nodes_map[member_id]
                        weight += self._calculate_weight(member_node, weight_func)
                G.nodes[node_id]["weight"] = weight
            else:
                # Handle regular node
                if node_id in self.nodes_map:
                    G.nodes[node_id]["weight"] = self._calculate_weight(self.nodes_map[node_id], weight_func)
                else:
                    # Use default weight if node not found
                    G.nodes[node_id]["weight"] = 1
        
        return G
    
    def _calculate_weight(self, node: Dict[str, Any], weight_func: str) -> float:
        """Calculate the weight of a node based on the specified function.
        
        Args:
            node: Node dictionary
            weight_func: Weight function to use (loc, calls, churn)
            
        Returns:
            Node weight
        """
        # Validate node data
        if not isinstance(node, dict):
            return 1
            
        if weight_func == "loc":
            # Weight based on uncovered lines of code
            properties = node.get("properties", {})
            if not isinstance(properties, dict):
                return 1
                
            total_loc = properties.get("loc", 0)
            if not isinstance(total_loc, (int, float)) or total_loc <= 0:
                return 1
                
            coverage_pct = properties.get("coverage", 0)
            if not isinstance(coverage_pct, (int, float)):
                coverage_pct = 0
                
            try:
                uncovered_loc = total_loc * (1 - coverage_pct / 100) if coverage_pct is not None else total_loc
                return max(uncovered_loc, 0.1)  # Ensure positive weight
            except (TypeError, ZeroDivisionError):
                return 1
                
        elif weight_func == "calls":
            # Weight based on number of incoming calls
            calls_in = node.get("calls_in", 0)
            if not isinstance(calls_in, (int, float)) or calls_in <= 0:
                return 1
            return calls_in
            
        elif weight_func == "churn":
            # Weight based on change frequency (placeholder)
            properties = node.get("properties", {})
            if not isinstance(properties, dict):
                return 1
                
            churn = properties.get("churn", 1)
            if not isinstance(churn, (int, float)) or churn <= 0:
                return 1
            return churn
            
        else:
            # Default weight
            return 1
    
    def _longest_path_scores(self, G: nx.DiGraph) -> Dict[str, float]:
        """Calculate longest path scores using dynamic programming.
        
        Args:
            G: Weighted NetworkX DiGraph
            
        Returns:
            Dictionary mapping node IDs to scores
        """
        try:
            # Check for cycles before attempting topological sort
            if not nx.is_directed_acyclic_graph(G):
                logger.error("Graph contains cycles, cannot perform topological sort")
                # For graphs with cycles, use a simpler approach based on node weights and degree
                scores = {}
                for node_id in G.nodes:
                    node_data = G.nodes[node_id]
                    # Base score is the node weight
                    weight = 1
                    if isinstance(node_data, dict):
                        weight = node_data.get("weight", 1)
                    
                    # Add a factor for incoming and outgoing edges
                    in_degree = G.in_degree(node_id)
                    out_degree = G.out_degree(node_id)
                    connectivity_factor = 1 + (in_degree + out_degree) / 10.0
                    
                    scores[node_id] = weight * connectivity_factor
                return scores
                
            # If no cycles, proceed with topological sort algorithm
            topo_order = list(nx.topological_sort(G))
            
            # Initialize scores with node weights
            scores = {}
            for node_id in topo_order:
                node_data = G.nodes[node_id]
                if isinstance(node_data, dict):
                    scores[node_id] = node_data.get("weight", 0)
                else:
                    scores[node_id] = 0
                    logger.warning(f"No data dictionary for node {node_id}")
            
            # Dynamic programming: for each node, update scores of successors
            for node_id in topo_order:
                node_score = scores[node_id]
                for successor in G.successors(node_id):
                    successor_data = G.nodes[successor]
                    successor_weight = 0
                    if isinstance(successor_data, dict):
                        successor_weight = successor_data.get("weight", 0)
                    
                    # Update the score if the path through current node is longer
                    scores[successor] = max(scores[successor], node_score + successor_weight)
            
            return scores
        except Exception as e:
            logger.error(f"Error calculating longest path scores: {str(e)}")
            # Return a fallback scores dictionary based on node weights only
            scores = {}
            for node_id in G.nodes:
                node_data = G.nodes[node_id]
                if isinstance(node_data, dict):
                    scores[node_id] = node_data.get("weight", 1)
                else:
                    scores[node_id] = 1
            return scores
    
    def _rank_critical_nodes(self, G: nx.DiGraph, scores: Dict[str, float], n: int) -> List[Dict[str, Any]]:
        """Rank nodes by criticality score.
        
        Args:
            G: NetworkX DiGraph
            scores: Dictionary mapping node IDs to scores
            n: Number of nodes to return
            
        Returns:
            List of critical nodes with risk scores
        """
        # Calculate risk scores: longest_path_score × (1 - coverage_pct)
        risk_scores = {}
        for node_id in G.nodes:
            # Add defensive check to make sure G.nodes[node_id] returns a dictionary not a string
            node_data = G.nodes[node_id]
            if not isinstance(node_data, dict):
                logger.warning(f"Skipping non-dictionary node data for node_id {node_id}")
                continue
                
            if node_data.get("is_scc", False):
                # Handle super-node (SCC)
                members = node_data.get("members", [])
                # Use average coverage for SCC members
                coverage_sum = 0
                count = 0
                for member_id in members:
                    if member_id in self.nodes_map:
                        member_node = self.nodes_map[member_id]
                        properties = member_node.get("properties", {})
                        coverage_pct = properties.get("coverage", 0)
                        coverage_sum += coverage_pct
                        count += 1
                avg_coverage = coverage_sum / max(count, 1)
                risk_scores[node_id] = scores[node_id] * (1 - avg_coverage / 100)
            else:
                # Handle regular node
                if node_id in self.nodes_map:
                    properties = self.nodes_map[node_id].get("properties", {})
                    # Safely get coverage value (default to 0 if not found)
                    coverage_pct = properties.get("coverage", 0)
                    if not isinstance(coverage_pct, (int, float)):
                        coverage_pct = 0
                    
                    # Calculate risk score - higher score for lower coverage
                    try:
                        risk_scores[node_id] = scores[node_id] * (1 - coverage_pct / 100)
                    except ZeroDivisionError:
                        risk_scores[node_id] = scores[node_id]
                else:
                    # Use default if node not found
                    risk_scores[node_id] = scores[node_id]
        
        # Sort nodes by risk score (descending)
        ranked_ids = sorted(risk_scores.keys(), key=lambda x: risk_scores[x], reverse=True)
        
        # Build result list with metadata
        result = []
        for rank, node_id in enumerate(ranked_ids[:n], 1):
            node_data = {
                "rank": rank,
                "node_id": node_id,
                "risk_score": risk_scores[node_id]
            }
            
            # Add defensive check to ensure G.nodes[node_id] returns a dictionary
            g_node_data = G.nodes[node_id]
            if not isinstance(g_node_data, dict):
                logger.warning(f"Skipping metadata for non-dictionary node data for node_id {node_id}")
                result.append(node_data)
                continue
            
            if g_node_data.get("is_scc", False):
                # Handle super-node (SCC)
                members = g_node_data.get("members", [])
                node_data["is_scc"] = True
                node_data["members"] = members
                
                # Aggregate coverage and line info from members
                missing_lines = []
                coverage_values = []
                for member_id in members:
                    if member_id in self.nodes_map:
                        member_node = self.nodes_map[member_id]
                        properties = member_node.get("properties", {})
                        coverage_pct = properties.get("coverage", 0)
                        coverage_values.append(coverage_pct)
                        
                        # Add missing lines
                        if "missing_lines" in properties:
                            missing_lines.extend(properties["missing_lines"])
                
                # Calculate average coverage
                node_data["coverage_pct"] = sum(coverage_values) / max(len(coverage_values), 1)
                node_data["missing_lines"] = missing_lines
                
                # Count calls in/out for SCC
                calls_in = sum(1 for u, v in G.in_edges(node_id))
                calls_out = sum(1 for u, v in G.out_edges(node_id))
                node_data["calls_in"] = calls_in
                node_data["calls_out"] = calls_out
            else:
                # Handle regular node
                if node_id in self.nodes_map:
                    node = self.nodes_map[node_id]
                    properties = node.get("properties", {})
                    
                    # Get coverage percentage with safety checks
                    coverage_pct = properties.get("coverage")
                    if not isinstance(coverage_pct, (int, float)):
                        coverage_pct = 0
                    node_data["coverage_pct"] = coverage_pct
                    
                    # Get missing lines
                    missing_lines = properties.get("missing_lines", [])
                    if not isinstance(missing_lines, list):
                        missing_lines = []
                    node_data["missing_lines"] = missing_lines
                    
                    # Count calls in/out
                    calls_in = sum(1 for u, v in G.in_edges(node_id))
                    calls_out = sum(1 for u, v in G.out_edges(node_id))
                    node_data["calls_in"] = calls_in
                    node_data["calls_out"] = calls_out
                    
                    # Add file path if available (normalize path)
                    if "file_path" in node:
                        file_path = node["file_path"]
                        # Strip absolute path if present to match expected format
                        if file_path and isinstance(file_path, str):
                            file_parts = file_path.split('/')
                            if 'flask' in file_parts:
                                # Get the path after 'flask'
                                idx = file_parts.index('flask')
                                if idx + 1 < len(file_parts):
                                    file_path = '/'.join(file_parts[idx+1:])
                        node_data["file_path"] = file_path
                    
                    # Add name if available
                    if "name" in node:
                        node_data["name"] = node["name"]
            
            result.append(node_data)
        
        return result
    
    def _write_output(self, ranked_nodes: List[Dict[str, Any]], output_file: Path) -> None:
        """Write ranked nodes to output file.
        
        Args:
            ranked_nodes: List of ranked node dictionaries
            output_file: Path to output file
        """
        output = {
            "version": "K1",
            "nodes": ranked_nodes
        }
        
        try:
            # Ensure parent directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            
            logger.info(f"Critical path data written to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write output: {str(e)}") 