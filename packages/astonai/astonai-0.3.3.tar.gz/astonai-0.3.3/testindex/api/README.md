# Coverage Map API

The Coverage Map API provides a REST interface and web UI for visualizing code coverage gaps detected by the Gap Detector.

## Features

- REST API for retrieving coverage data by file or directory
- HTML/JS-based heat map visualization of coverage
- File tree navigation
- Red-green coloring based on coverage percentage
- Detailed gap information including line ranges

## Usage

### Starting the API Server

```bash
# Start the API server on the default port (8080)
python scripts/run_coverage_api.py

# Start on a specific port
python scripts/run_coverage_api.py --port 5000

# Enable debug mode
python scripts/run_coverage_api.py --debug

# Use mock data (no Neo4j connection required)
python scripts/run_coverage_api.py --mock
```

### Accessing the UI

Once the server is running, you can access the web UI at:

```
http://localhost:8080/
```

To use mock data in the UI (useful for testing without Neo4j):
```
http://localhost:8080/?mock=true
```

### API Endpoints

#### GET /coverage-map

Get coverage data for a file or directory.

**Query Parameters:**

- `path`: The file or directory path to get coverage for (required)
- `mock`: Set to 'true' to use mock data instead of querying Neo4j (optional)

**Example Response for File:**

```json
{
  "path": "src/main.py",
  "lines_total": 100,
  "lines_covered": 75,
  "coverage_percentage": 75.0,
  "gaps": [
    {
      "impl_id": "unique-id",
      "path": "src/main.py",
      "line_start": 10,
      "line_end": 20,
      "coverage": 0.0
    }
  ]
}
```

**Example Response for Directory:**

```json
{
  "path": "src",
  "files_count": 3,
  "lines_total": 300,
  "lines_covered": 225,
  "coverage_percentage": 75.0,
  "files": [
    {
      "path": "src/main.py",
      "lines_total": 100,
      "lines_covered": 75,
      "coverage_percentage": 75.0,
      "gaps": [...]
    },
    ...
  ]
}
```

## Performance Testing

You can test the API performance against the load time KPI (<200ms) using the provided script:

```bash
# Test performance for specific paths
python scripts/test_api_performance.py --paths src src/main.py

# Save results to a file
python scripts/test_api_performance.py --paths src --output results.json

# Run more requests for better statistics
python scripts/test_api_performance.py --paths src --requests 50
```

## Running the Full Pipeline

The `run_heat_map_test.sh` script executes the full pipeline:

```bash
# Run with default settings
./scripts/run_heat_map_test.sh

# Run with debug mode
./scripts/run_heat_map_test.sh --debug

# Run on a specific port
./scripts/run_heat_map_test.sh --port 9000

# Run with mock data (no Neo4j required)
./scripts/run_heat_map_test.sh --mock
```

## Dependencies

- Flask
- Flask-CORS
- Neo4j (for accessing the Knowledge Graph, optional when using mock mode)

## Architecture

The Coverage Map API has two main components:

1. **REST API**: Provides endpoints for retrieving coverage data
2. **Web UI**: HTML/JS interface for visualizing coverage data

The API queries the Neo4j Knowledge Graph to retrieve implementation and gap data, then transforms it into a format suitable for visualization.

## Troubleshooting

If you encounter port conflicts (especially on macOS where AirPlay uses port 5000), you can:

1. Use a different port with `--port` option
2. Disable AirPlay Receiver in System Settings > AirDrop & Handoff
3. Set the `FLASK_RUN_PORT` environment variable

### Neo4j Connection Issues

If you encounter Neo4j connection issues:

1. Make sure Neo4j is running and accessible
2. Check your Neo4j credentials in the environment variables
3. Run the API in mock mode with `--mock` to use generated test data
4. Use the web UI with `?mock=true` parameter to bypass Neo4j 