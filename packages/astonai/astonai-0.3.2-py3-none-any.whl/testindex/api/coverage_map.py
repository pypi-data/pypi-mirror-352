"""
Coverage Map API

Implements the REST API for serving coverage data to the heat-map UI.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS

from testindex.analysis.coverage.gap_detector import GapDetector
from testindex.analysis.coverage.utils import SimpleNeo4jClient
from testindex_knowledge_contract.schema import (
    IMPL_LABEL, GAP_LABEL, PROP_ID, PROP_PATH, PROP_START, PROP_END, PROP_COVER
)
from testindex.api.github_bot import github_bot

# Define relationship type that might not be in the schema contract
REL_HAS_GAP = "HAS_GAP"

# Setup logging
logger = logging.getLogger(__name__)

# Find the path to the static directory
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, 'static')

# Create Flask app with static folder config
app = Flask(__name__, static_folder=static_folder)
CORS(app)  # Enable CORS for all routes

# Register the GitHub webhook blueprint
app.register_blueprint(github_bot, url_prefix='/api')


class CoverageMapAPI:
    """API handler for coverage map data."""
    
    def __init__(self, neo4j_client: Optional[SimpleNeo4jClient] = None):
        """Initialize the coverage map API.
        
        Args:
            neo4j_client: Neo4j client for Knowledge Graph access
        """
        self.neo4j_client = neo4j_client or SimpleNeo4jClient()
        self.gap_detector = GapDetector(neo4j_client=self.neo4j_client)
    
    def get_file_coverage(self, file_path: str) -> Dict[str, Any]:
        """Get coverage data for a specific file path.
        
        Args:
            file_path: Path to the file to get coverage for
            
        Returns:
            Dictionary with coverage data in the format:
            {
                "path": "path/to/file",
                "lines_total": 100,
                "lines_covered": 75,
                "coverage_percentage": 75.0,
                "gaps": [
                    {
                        "impl_id": "unique-id",
                        "path": "path/to/file",
                        "line_start": 10,
                        "line_end": 20,
                        "coverage": 0.0
                    }
                ]
            }
        """
        # Query for all implementations in the file
        all_impl_query = f"""
        MATCH (impl:{IMPL_LABEL})
        WHERE impl.{PROP_PATH} = $path
        RETURN 
            impl.{PROP_ID} as id,
            impl.{PROP_PATH} as path,
            impl.{PROP_START} as line_start,
            impl.{PROP_END} as line_end,
            impl.{PROP_COVER} as coverage
        """
        
        # Query for gaps in the file
        gaps_query = f"""
        MATCH (impl:{IMPL_LABEL})-[:{REL_HAS_GAP}]->(gap:{GAP_LABEL})
        WHERE impl.{PROP_PATH} = $path
        RETURN 
            gap.{PROP_ID} as impl_id,
            gap.path as path,
            gap.line_start as line_start,
            gap.line_end as line_end,
            gap.coverage as coverage
        """
        
        try:
            # Get all implementations in the file
            all_impls = self.neo4j_client.run_query(all_impl_query, {'path': file_path})
            
            if not all_impls:
                return {
                    "path": file_path,
                    "lines_total": 0,
                    "lines_covered": 0,
                    "coverage_percentage": 0.0,
                    "gaps": []
                }
            
            # Calculate total and covered lines
            total_lines = 0
            covered_lines = 0
            
            for impl in all_impls:
                impl_lines = impl['line_end'] - impl['line_start'] + 1
                total_lines += impl_lines
                covered_lines += impl_lines * (impl['coverage'] / 100)
            
            # Get gaps in the file
            gaps = self.neo4j_client.run_query(gaps_query, {'path': file_path})
            
            # Calculate coverage percentage
            coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            
            return {
                "path": file_path,
                "lines_total": total_lines,
                "lines_covered": int(covered_lines),
                "coverage_percentage": round(coverage_percentage, 2),
                "gaps": gaps
            }
            
        except Exception as e:
            logger.error(f"Error getting coverage for {file_path}: {str(e)}")
            raise
    
    def get_directory_coverage(self, directory_path: str) -> Dict[str, Any]:
        """Get aggregate coverage data for a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Dictionary with coverage data for the directory and its files
        """
        # Query for all files in the directory
        files_query = f"""
        MATCH (impl:{IMPL_LABEL})
        WHERE impl.{PROP_PATH} STARTS WITH $path
        RETURN DISTINCT impl.{PROP_PATH} as path
        """
        
        try:
            # Get all files in the directory
            files = self.neo4j_client.run_query(files_query, {'path': directory_path})
            file_paths = [file['path'] for file in files]
            
            # Get coverage for each file
            files_coverage = []
            total_lines = 0
            total_covered = 0
            
            for file_path in file_paths:
                file_coverage = self.get_file_coverage(file_path)
                files_coverage.append(file_coverage)
                
                total_lines += file_coverage['lines_total']
                total_covered += file_coverage['lines_covered']
            
            # Calculate directory coverage percentage
            dir_coverage = (total_covered / total_lines * 100) if total_lines > 0 else 0
            
            return {
                "path": directory_path,
                "files_count": len(file_paths),
                "lines_total": total_lines,
                "lines_covered": total_covered,
                "coverage_percentage": round(dir_coverage, 2),
                "files": files_coverage
            }
            
        except Exception as e:
            logger.error(f"Error getting coverage for directory {directory_path}: {str(e)}")
            raise


# Create API handler
coverage_api = CoverageMapAPI()


# Serve static files
@app.route('/')
def index():
    """Serve the index.html file."""
    return send_from_directory(static_folder, 'index.html')


@app.route('/<path:path>')
def static_file(path):
    """Serve static files."""
    if os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return "File not found", 404


@app.route('/coverage-map', methods=['GET'])
def get_coverage_map():
    """Endpoint for getting coverage data for a file or directory.
    
    Query parameters:
        path: Path to file or directory (required)
        mock: Set to 'true' to use mock data (for testing without Neo4j)
        
    Returns:
        JSON response with coverage data
    """
    path = request.args.get('path')
    use_mock = (request.args.get('mock', '').lower() == 'true' or 
                os.environ.get('USE_MOCK_DATA', '').lower() == 'true')
    
    if not path:
        return jsonify({"error": "Path parameter is required"}), 400
    
    try:
        # Use mock data if requested or in case of Neo4j connection failure
        if use_mock:
            return get_mock_data(path)
            
        # Determine if path is a file or directory
        # For simplicity, we'll consider paths without '.' in the last segment as directories
        if '.' in os.path.basename(path):
            # It's a file
            coverage_data = coverage_api.get_file_coverage(path)
        else:
            # It's a directory
            coverage_data = coverage_api.get_directory_coverage(path)
        
        return jsonify(coverage_data)
    
    except Exception as e:
        error_message = str(e)
        error_type = "Database Error" if "connect" in error_message.lower() else "Server Error"
        
        logger.error(f"Error processing request: {error_message}")
        
        # If Neo4j connection fails and mock wasn't explicitly requested, try using mock data
        if ("connect" in error_message.lower() or "connection refused" in error_message.lower()):
            logger.info("Database connection failed, falling back to mock data")
            return get_mock_data(path)
        
        response = {
            "error": f"{error_type}: {error_message}",
            "suggestion": get_error_suggestion(error_message)
        }
        
        return jsonify(response), 500


def get_error_suggestion(error_message):
    """Get a helpful suggestion based on the error message.
    
    Args:
        error_message: The error message string
        
    Returns:
        A suggestion string
    """
    error_lower = error_message.lower()
    
    if "couldn't connect" in error_lower or "connection refused" in error_lower:
        return ("Neo4j database connection failed. Please make sure Neo4j is running "
                "and check your connection settings (host, port, credentials).")
    elif "authorization" in error_lower or "authentication" in error_lower:
        return "Neo4j authentication failed. Please check your username and password."
    elif "cypher" in error_lower:
        return "Cypher query error. There might be a syntax error in the query."
    else:
        return "Please check server logs for more details."


def get_mock_data(path):
    """Generate mock data for testing without Neo4j.
    
    Args:
        path: File or directory path
        
    Returns:
        Mock coverage data response
    """
    # Check if it's a file or directory based on extension
    if '.' in os.path.basename(path):
        # It's a file
        return jsonify({
            "path": path,
            "lines_total": 100,
            "lines_covered": 75,
            "coverage_percentage": 75.0,
            "gaps": [
                {
                    "impl_id": "mock-id-1",
                    "path": path,
                    "line_start": 10,
                    "line_end": 20,
                    "coverage": 0.0
                },
                {
                    "impl_id": "mock-id-2",
                    "path": path,
                    "line_start": 50,
                    "line_end": 55,
                    "coverage": 0.0
                }
            ]
        })
    else:
        # It's a directory
        # Create consistent mock files based on the directory name
        # This ensures navigation works correctly in the UI
        mock_files = []
        for i in range(1, 4):
            file_path = f"{path}/file{i}.py"
            mock_files.append({
                "path": file_path,
                "lines_total": 100,
                "lines_covered": 75 + (i * 5),  # Vary coverage slightly
                "coverage_percentage": 75.0 + (i * 5),
                "gaps": []  # Empty gaps for simplicity
            })
        
        return jsonify({
            "path": path,
            "files_count": len(mock_files),
            "lines_total": 300,
            "lines_covered": 225,
            "coverage_percentage": 75.0,
            "files": mock_files
        })


def run_api_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the Flask API server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Whether to run in debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run server
    run_api_server(debug=True) 