"""
Viewer asset packager for knowledge graph visualization.

This module manages the static HTML/JS/CSS assets for the graph viewer.
"""
import os
import shutil
from pathlib import Path
from typing import Optional

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.core.exceptions import CLIError
from testindex.core.utils import ensure_directory

# Set up logger
logger = get_logger(__name__)

# Default viewer assets
DEFAULT_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Knowledge Graph Viewer</title>
    <meta charset="utf-8">
    <style>
        body { margin: 0; font-family: Arial, sans-serif; }
        #graph { width: 100vw; height: 100vh; }
        .controls {
            position: fixed;
            top: 10px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .controls label { margin-right: 10px; }
    </style>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <div class="controls">
        <label><input type="checkbox" id="showCalls" checked> Show CALLS</label>
        <label><input type="checkbox" id="showImports" checked> Show IMPORTS</label>
        <input type="text" id="search" placeholder="Search nodes...">
    </div>
    <div id="graph"></div>
    <script src="viewer.js"></script>
</body>
</html>"""

DEFAULT_JS_TEMPLATE = """// Knowledge Graph Viewer
const width = window.innerWidth;
const height = window.innerHeight;

// Create SVG container
const svg = d3.select('#graph')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

// Add zoom behavior
const g = svg.append('g');
svg.call(d3.zoom()
    .extent([[0, 0], [width, height]])
    .scaleExtent([0.1, 4])
    .on('zoom', ({transform}) => g.attr('transform', transform)));

// Graph data (embedded)
const dotContent = `%DOT_CONTENT%`;

// Simple DOT parser (handles basic subset needed for our graphs)
function parseDot(dot) {
    const nodes = new Map();
    const edges = [];
    
    // Extract node and edge definitions
    const lines = dot.split('\\n');
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('//')) continue;
        
        // Node definition
        const nodeMatch = trimmed.match(/"([^"]+)"\\s*\\[(.*?)\\]/);
        if (nodeMatch) {
            const [_, id, attrs] = nodeMatch;
            const labelMatch = attrs.match(/label="([^"]+)"/);
            const shapeMatch = attrs.match(/shape=(\\w+)/);
            nodes.set(id, {
                id,
                label: labelMatch ? labelMatch[1] : id,
                shape: shapeMatch ? shapeMatch[1] : 'circle'
            });
            continue;
        }
        
        // Edge definition
        const edgeMatch = trimmed.match(/"([^"]+)"\\s*->\\s*"([^"]+)"\\s*\\[(.*?)\\]/);
        if (edgeMatch) {
            const [_, source, target, attrs] = edgeMatch;
            const labelMatch = attrs.match(/label="([^"]+)"/);
            const colorMatch = attrs.match(/color=(\\w+)/);
            edges.push({
                source,
                target,
                type: labelMatch ? labelMatch[1] : '',
                color: colorMatch ? colorMatch[1] : 'gray'
            });
        }
    }
    
    return {
        nodes: Array.from(nodes.values()),
        edges
    };
}

// Parse graph data
const graph = parseDot(dotContent);

// Create force simulation
const simulation = d3.forceSimulation(graph.nodes)
    .force('link', d3.forceLink(graph.edges).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-1000))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(50));

// Draw edges
const edges = g.append('g')
    .selectAll('line')
    .data(graph.edges)
    .join('line')
    .attr('stroke', d => d.color)
    .attr('stroke-width', 2)
    .attr('marker-end', 'url(#arrow)');

// Draw nodes
const nodes = g.append('g')
    .selectAll('g')
    .data(graph.nodes)
    .join('g')
    .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

// Add shapes based on node type
nodes.each(function(d) {
    const node = d3.select(this);
    if (d.shape === 'box') {
        node.append('rect')
            .attr('width', 120)
            .attr('height', 40)
            .attr('x', -60)
            .attr('y', -20)
            .attr('fill', '#fff')
            .attr('stroke', '#000');
    } else {
        node.append('circle')
            .attr('r', 20)
            .attr('fill', '#fff')
            .attr('stroke', '#000');
    }
});

// Add labels
nodes.append('text')
    .text(d => d.label)
    .attr('text-anchor', 'middle')
    .attr('dy', '.35em')
    .attr('font-size', '12px');

// Add arrow marker
svg.append('defs').append('marker')
    .attr('id', 'arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 25)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#999');

// Update positions on each tick
simulation.on('tick', () => {
    edges
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
    
    nodes.attr('transform', d => `translate(${d.x},${d.y})`);
});

// Drag handlers
function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}

function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
}

// Edge type filtering
d3.select('#showCalls').on('change', function() {
    const show = this.checked;
    edges.filter(d => d.type === 'CALLS')
        .style('display', show ? null : 'none');
});

d3.select('#showImports').on('change', function() {
    const show = this.checked;
    edges.filter(d => d.type === 'IMPORTS')
        .style('display', show ? null : 'none');
});

// Node search
d3.select('#search').on('input', function() {
    const term = this.value.toLowerCase();
    nodes.style('opacity', d => 
        term === '' || d.label.toLowerCase().includes(term) ? 1 : 0.2
    );
});"""

class ViewerPackager:
    """Manages the static assets for the graph viewer."""
    
    @staticmethod
    def ensure_viewer_assets(target_dir: Path) -> None:
        """Ensure viewer assets are present in target directory.
        
        Args:
            target_dir: Directory to place viewer assets
            
        Raises:
            CLIError: If assets cannot be created
        """
        try:
            # Create target directory
            ensure_directory(target_dir)
            
            # Read graph.dot content
            dot_file = target_dir / "graph.dot"
            if not dot_file.exists():
                raise CLIError(f"Graph file not found: {dot_file}")
                
            dot_content = dot_file.read_text()
            
            # Write HTML file
            html_file = target_dir / "index.html"
            with open(html_file, 'w') as f:
                f.write(DEFAULT_HTML)
                
            # Write JS file with embedded graph data
            js_file = target_dir / "viewer.js"
            js_content = DEFAULT_JS_TEMPLATE.replace('%DOT_CONTENT%', dot_content.replace('\\', '\\\\').replace('`', '\\`'))
            with open(js_file, 'w') as f:
                f.write(js_content)
                
            logger.info(f"Created viewer assets in {target_dir}")
            
        except Exception as e:
            error_msg = f"Failed to create viewer assets: {e}"
            logger.error(error_msg)
            raise CLIError(error_msg) 