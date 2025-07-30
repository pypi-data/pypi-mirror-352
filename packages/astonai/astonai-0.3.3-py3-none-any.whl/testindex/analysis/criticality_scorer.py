"""
Criticality Scorer for TestIndex.

This module implements criticality scoring for code nodes based on 
degree centrality and call depth to replace flat node counting in 
regression analysis and test suggestions.
"""

import json
import time
import yaml
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

import networkx as nx
import numpy as np

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.core.exceptions import AstonError

logger = get_logger(__name__)


@dataclass
class CriticalityWeights:
    """Configuration for criticality scoring weights."""
    centrality_weight: float = 0.7
    depth_weight: float = 0.3
    entry_point_patterns: List[str] = None
    max_call_depth: int = 20
    min_graph_size: int = 5
    enable_caching: bool = True
    auto_invalidate_cache: bool = True
    max_batch_size: int = 1000
    verbose_logging: bool = False
    export_intermediate_data: bool = False

    def __post_init__(self):
        if self.entry_point_patterns is None:
            self.entry_point_patterns = [
                "main", "test_*", "*_handler", "*_endpoint", 
                "*_view", "handle_*"
            ]


class CriticalityError(AstonError):
    """Exception raised when criticality calculation fails."""
    pass


class CriticalityScorer:
    """Calculates criticality scores for code nodes using graph analytics."""
    
    def __init__(self, weights: Optional[CriticalityWeights] = None):
        """Initialize the criticality scorer.
        
        Args:
            weights: Custom weight configuration, uses defaults if None
        """
        self.weights = weights or CriticalityWeights()
        self._node_scores_cache = {}
        self._graph_hash = None
        self._centrality_cache = {}
        self._depth_cache = {}
        
    @classmethod
    def from_config_file(cls, config_path: Optional[Union[str, Path]] = None) -> 'CriticalityScorer':
        """Create scorer from YAML configuration file.
        
        Args:
            config_path: Path to weights config file, uses default if None
            
        Returns:
            CriticalityScorer instance
        """
        if config_path is None:
            # Look for user config first, then fall back to default
            resolver = PathResolver()
            user_config = resolver.repo_root() / "criticality_weights.yaml"
            if user_config.exists():
                config_path = user_config
            else:
                config_path = Path(__file__).parent.parent / "config" / "criticality_weights.yaml"
        
        config_path = Path(config_path)
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Extract weights configuration
            weights = CriticalityWeights(
                centrality_weight=config_data.get('centrality_weight', 0.7),
                depth_weight=config_data.get('depth_weight', 0.3),
                entry_point_patterns=config_data.get('entry_point_patterns', None),
                max_call_depth=config_data.get('normalization', {}).get('max_call_depth', 20),
                min_graph_size=config_data.get('normalization', {}).get('min_graph_size', 5),
                enable_caching=config_data.get('performance', {}).get('enable_caching', True),
                auto_invalidate_cache=config_data.get('performance', {}).get('auto_invalidate_cache', True),
                max_batch_size=config_data.get('performance', {}).get('max_batch_size', 1000),
                verbose_logging=config_data.get('debug', {}).get('verbose_logging', False),
                export_intermediate_data=config_data.get('debug', {}).get('export_intermediate_data', False)
            )
            
            logger.info(f"Loaded criticality weights from {config_path}")
            return cls(weights)
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise CriticalityError(f"Failed to load criticality config: {str(e)}")
    
    def calculate_criticality_scores(self, 
                                   nodes: List[Dict[str, Any]], 
                                   edges: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate criticality scores for all nodes.
        
        Args:
            nodes: List of node dictionaries with id, name, file_path
            edges: List of edge dictionaries with source_id, target_id
            
        Returns:
            Dictionary mapping node_id to criticality score
        """
        start_time = time.time()
        
        if not nodes:
            logger.warning("No nodes provided for criticality calculation")
            return {}
        
        # Build graph
        graph = self._build_graph(nodes, edges)
        
        if len(graph.nodes) < self.weights.min_graph_size:
            logger.warning(f"Graph too small ({len(graph.nodes)} nodes) for meaningful centrality")
            return {node['id']: 0.0 for node in nodes}
        
        # Check cache validity
        graph_hash = self._compute_graph_hash(nodes, edges)
        if (self.weights.enable_caching and 
            self._graph_hash == graph_hash and 
            self._node_scores_cache):
            logger.debug("Using cached criticality scores")
            return self._node_scores_cache.copy()
        
        # Calculate components
        centrality_scores = self._calculate_centrality(graph)
        depth_scores = self._calculate_call_depth(graph, nodes)
        
        # Combine scores
        criticality_scores = {}
        for node in nodes:
            node_id = node['id']
            centrality = centrality_scores.get(node_id, 0.0)
            depth = depth_scores.get(node_id, 0.0)
            
            criticality = (self.weights.centrality_weight * centrality + 
                          self.weights.depth_weight * depth)
            
            criticality_scores[node_id] = round(criticality, 4)
            
            if self.weights.verbose_logging:
                logger.debug(f"Node {node_id}: centrality={centrality:.4f}, "
                           f"depth={depth:.4f}, criticality={criticality:.4f}")
        
        # Update cache
        if self.weights.enable_caching:
            self._node_scores_cache = criticality_scores.copy()
            self._graph_hash = graph_hash
        
        # Export intermediate data if requested
        if self.weights.export_intermediate_data:
            self._export_intermediate_data(centrality_scores, depth_scores, criticality_scores)
        
        duration = time.time() - start_time
        logger.info(f"Calculated criticality for {len(nodes)} nodes in {duration:.2f}s")
        
        return criticality_scores
    
    def get_top_critical_nodes(self, 
                              nodes: List[Dict[str, Any]], 
                              edges: List[Dict[str, Any]], 
                              top_k: int = 10) -> List[Dict[str, Any]]:
        """Get the top-k most critical nodes with their scores.
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries  
            top_k: Number of top nodes to return
            
        Returns:
            List of node dictionaries with added 'criticality_score' field
        """
        scores = self.calculate_criticality_scores(nodes, edges)
        
        # Add scores to nodes and sort by criticality
        nodes_with_scores = []
        for node in nodes:
            node_copy = node.copy()
            node_copy['criticality_score'] = scores.get(node['id'], 0.0)
            nodes_with_scores.append(node_copy)
        
        # Sort by criticality score descending
        nodes_with_scores.sort(key=lambda x: x['criticality_score'], reverse=True)
        
        return nodes_with_scores[:top_k]
    
    def calculate_weighted_impact_score(self, 
                                      impacted_nodes: List[Dict[str, Any]], 
                                      all_nodes: List[Dict[str, Any]], 
                                      edges: List[Dict[str, Any]]) -> float:
        """Calculate weighted impact score for regression analysis.
        
        Args:
            impacted_nodes: List of nodes affected by changes
            all_nodes: Complete list of nodes for scoring context
            edges: List of edges for graph construction
            
        Returns:
            Weighted impact score (0.0 to 1.0)
        """
        if not impacted_nodes:
            return 0.0
        
        # Get criticality scores for all nodes
        all_scores = self.calculate_criticality_scores(all_nodes, edges)
        
        # Calculate weighted score for impacted nodes
        impacted_scores = []
        for node in impacted_nodes:
            node_id = node.get('id')
            if node_id in all_scores:
                impacted_scores.append(all_scores[node_id])
        
        if not impacted_scores:
            return 0.0
        
        # Use mean criticality of impacted nodes as weighted score
        weighted_score = np.mean(impacted_scores)
        
        # Normalize to 0-1 range (criticality scores should already be in this range)
        return min(1.0, max(0.0, weighted_score))
    
    def _build_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build NetworkX graph from nodes and edges.
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
            
        Returns:
            NetworkX DiGraph
        """
        graph = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            node_id = node['id']
            graph.add_node(node_id, **node)
        
        # Add edges
        for edge in edges:
            source_id = edge.get('source_id') or edge.get('src') or edge.get('source')
            target_id = edge.get('target_id') or edge.get('dst') or edge.get('target')
            
            if source_id and target_id and source_id in graph.nodes and target_id in graph.nodes:
                graph.add_edge(source_id, target_id, **edge)
        
        logger.debug(f"Built graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        return graph
    
    def _calculate_centrality(self, graph: nx.DiGraph) -> Dict[str, float]:
        """Calculate degree centrality for all nodes.
        
        Args:
            graph: NetworkX DiGraph
            
        Returns:
            Dictionary mapping node_id to centrality score
        """
        try:
            # Use degree centrality (combines in-degree and out-degree)
            centrality = nx.degree_centrality(graph)
            
            if self.weights.verbose_logging:
                max_centrality = max(centrality.values()) if centrality else 0
                logger.debug(f"Calculated centrality, max={max_centrality:.4f}")
            
            return centrality
            
        except Exception as e:
            logger.warning(f"Failed to calculate centrality: {e}")
            return {node: 0.0 for node in graph.nodes}
    
    def _calculate_call_depth(self, graph: nx.DiGraph, nodes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate normalized call depth from entry points.
        
        Args:
            graph: NetworkX DiGraph
            nodes: List of node dictionaries for entry point identification
            
        Returns:
            Dictionary mapping node_id to normalized depth score
        """
        try:
            # Identify entry points
            entry_points = self._find_entry_points(nodes)
            
            if not entry_points:
                logger.warning("No entry points found, using nodes with no incoming edges")
                entry_points = [node for node in graph.nodes if graph.in_degree(node) == 0]
            
            if not entry_points:
                logger.warning("No entry points available for depth calculation")
                return {node: 0.0 for node in graph.nodes}
            
            # Calculate shortest path lengths from all entry points
            depth_scores = {}
            for node in graph.nodes:
                min_depth = float('inf')
                
                for entry_point in entry_points:
                    if entry_point in graph.nodes:
                        try:
                            depth = nx.shortest_path_length(graph, source=entry_point, target=node)
                            min_depth = min(min_depth, depth)
                        except nx.NetworkXNoPath:
                            continue
                
                # Normalize depth score
                if min_depth == float('inf'):
                    depth_scores[node] = 0.0
                else:
                    # Normalize by max_call_depth (higher depth = higher score)
                    normalized_depth = min(min_depth / self.weights.max_call_depth, 1.0)
                    depth_scores[node] = normalized_depth
            
            if self.weights.verbose_logging:
                max_depth = max(depth_scores.values()) if depth_scores else 0
                logger.debug(f"Calculated call depth, max_normalized={max_depth:.4f}")
            
            return depth_scores
            
        except Exception as e:
            logger.warning(f"Failed to calculate call depth: {e}")
            return {node: 0.0 for node in graph.nodes}
    
    def _find_entry_points(self, nodes: List[Dict[str, Any]]) -> List[str]:
        """Find entry point nodes based on name patterns.
        
        Args:
            nodes: List of node dictionaries
            
        Returns:
            List of node IDs that match entry point patterns
        """
        entry_points = []
        
        for node in nodes:
            node_name = node.get('name', '')
            if not node_name:
                continue
            
            for pattern in self.weights.entry_point_patterns:
                if fnmatch.fnmatch(node_name, pattern):
                    entry_points.append(node['id'])
                    break
        
        if self.weights.verbose_logging:
            logger.debug(f"Found {len(entry_points)} entry points: {entry_points[:5]}...")
        
        return entry_points
    
    def _compute_graph_hash(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> int:
        """Compute hash for graph structure for cache invalidation.
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
            
        Returns:
            Hash value representing graph structure
        """
        node_ids = sorted([node['id'] for node in nodes])
        edge_pairs = sorted([(edge.get('source_id') or edge.get('src') or edge.get('source'), 
                            edge.get('target_id') or edge.get('dst') or edge.get('target')) 
                           for edge in edges])
        
        return hash((tuple(node_ids), tuple(edge_pairs)))
    
    def _export_intermediate_data(self, 
                                centrality_scores: Dict[str, float], 
                                depth_scores: Dict[str, float], 
                                criticality_scores: Dict[str, float]) -> None:
        """Export intermediate scoring data for analysis.
        
        Args:
            centrality_scores: Centrality scores by node_id
            depth_scores: Depth scores by node_id
            criticality_scores: Final criticality scores by node_id
        """
        try:
            resolver = PathResolver()
            output_file = resolver.knowledge_graph_dir() / "criticality_analysis.json"
            
            export_data = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "weights": asdict(self.weights),
                "centrality_scores": centrality_scores,
                "depth_scores": depth_scores, 
                "criticality_scores": criticality_scores,
                "statistics": {
                    "total_nodes": len(criticality_scores),
                    "max_centrality": max(centrality_scores.values()) if centrality_scores else 0,
                    "max_depth": max(depth_scores.values()) if depth_scores else 0,
                    "max_criticality": max(criticality_scores.values()) if criticality_scores else 0
                }
            }
            
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported criticality analysis to {output_file}")
            
        except Exception as e:
            logger.warning(f"Failed to export intermediate data: {e}")
    
    def invalidate_cache(self) -> None:
        """Manually invalidate criticality score cache."""
        self._node_scores_cache.clear()
        self._graph_hash = None
        self._centrality_cache.clear()
        self._depth_cache.clear()
        logger.debug("Criticality score cache invalidated")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_scores": len(self._node_scores_cache),
            "cache_enabled": self.weights.enable_caching,
            "graph_hash": self._graph_hash,
            "cache_valid": bool(self._graph_hash and self._node_scores_cache)
        } 