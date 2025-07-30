"""
DOT format exporter for knowledge graph visualization.

This module provides functionality to export the knowledge graph to Graphviz DOT format.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, TextIO

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.core.exceptions import CLIError

# Set up logger
logger = get_logger(__name__)

class DotExporter:
    """Exports knowledge graph to DOT format for visualization."""
    
    def __init__(self, edge_filter: Optional[List[str]] = None):
        """Initialize the DOT exporter.
        
        Args:
            edge_filter: List of edge types to include (e.g. ["CALLS", "IMPORTS"])
                       If None, all edge types are included.
        """
        self.edge_filter = edge_filter or ["CALLS", "IMPORTS"]
        
    def _node_attributes(self, node: Dict[str, Any]) -> str:
        """Get DOT attributes for a node based on its type.
        
        Args:
            node: Node dictionary from nodes.json
            
        Returns:
            str: DOT node attributes
        """
        node_type = node.get("type", "Unknown")
        label = node.get("name", "unknown")
        
        if node_type == "Module":
            return f'[shape=box,label="{label}"]'
        elif node_type == "Implementation":
            return f'[shape=ellipse,label="{label}"]'
        else:
            return f'[shape=diamond,label="{label}"]'
            
    def _edge_attributes(self, edge: Dict[str, Any]) -> str:
        """Get DOT attributes for an edge based on its type.
        
        Args:
            edge: Edge dictionary from edges.json
            
        Returns:
            str: DOT edge attributes
        """
        edge_type = edge.get("type", "Unknown")
        
        if edge_type == "CALLS":
            return '[color=darkgreen,label="CALLS"]'
        elif edge_type == "IMPORTS":
            return '[color=steelblue,label="IMPORTS"]'
        else:
            return '[color=gray]'
            
    def export_dot(self, output_file: Path) -> None:
        """Export the knowledge graph to DOT format.
        
        Args:
            output_file: Path to write the DOT file
            
        Raises:
            CLIError: If export fails
        """
        try:
            # Get paths using PathResolver
            kg_dir = PathResolver.knowledge_graph_dir()
            nodes_file = kg_dir / "nodes.json"
            edges_file = kg_dir / "edges.json"
            
            # Check if files exist
            if not nodes_file.exists():
                raise CLIError(f"Nodes file not found: {nodes_file}")
            if not edges_file.exists():
                raise CLIError(f"Edges file not found: {edges_file}")
                
            # Load nodes
            try:
                with open(nodes_file, 'r') as f:
                    nodes = json.load(f)
            except json.JSONDecodeError as e:
                raise CLIError(f"Invalid JSON in nodes file: {e}")
                
            # Load edges
            try:
                with open(edges_file, 'r') as f:
                    edges_data = json.load(f)
                    edges = edges_data.get("edges", [])
            except json.JSONDecodeError as e:
                raise CLIError(f"Invalid JSON in edges file: {e}")
                
            # Create output directory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)
                
            # Create DOT file
            with open(output_file, 'w') as f:
                # Write header
                f.write('strict digraph {\n')
                f.write('    // Graph attributes\n')
                f.write('    graph [rankdir=LR];\n')
                f.write('    node [fontname="Arial"];\n')
                f.write('    edge [fontname="Arial"];\n\n')
                
                # Write nodes
                f.write('    // Nodes\n')
                for node in nodes:
                    node_id = node.get("id", "unknown")
                    attrs = self._node_attributes(node)
                    f.write(f'    "{node_id}" {attrs};\n')
                    
                # Write edges
                f.write('\n    // Edges\n')
                for edge in edges:
                    # Skip if edge type not in filter
                    edge_type = edge.get("type")
                    if edge_type not in self.edge_filter:
                        continue
                        
                    src = edge.get("source", "unknown")
                    dst = edge.get("target", "unknown")
                    attrs = self._edge_attributes(edge)
                    f.write(f'    "{src}" -> "{dst}" {attrs};\n')
                    
                # Write footer
                f.write('}\n')
                
            logger.info(f"Exported graph to {output_file}")
            
        except CLIError:
            # Re-raise CLI errors
            raise
        except Exception as e:
            error_msg = f"Failed to export graph to DOT: {e}"
            logger.error(error_msg)
            raise CLIError(error_msg) 