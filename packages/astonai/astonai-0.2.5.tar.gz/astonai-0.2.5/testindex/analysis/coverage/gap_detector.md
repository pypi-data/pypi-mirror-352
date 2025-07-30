# Coverage Gap Detector

The Coverage Gap Detector is a tool for identifying implementations (functions, methods, classes) that have zero or low test coverage. It leverages the Knowledge Graph to find implementation nodes with coverage below a specified threshold, and can optionally store the results back into Neo4j as CoverageGap nodes.

## Installation

The Gap Detector is part of the testindex analysis package. Make sure you have:

1. Installed the required dependencies, including `testindex_knowledge_contract`
2. Configured Neo4j access (via environment variables or directly in code)

## Usage

### Command Line Interface

The Gap Detector can be run as a standalone tool using the `detect_gaps.py` script:

```bash
# Basic usage (outputs gaps.json with zero-coverage implementations)
python scripts/detect_gaps.py 

# Specify custom output file and threshold
python scripts/detect_gaps.py --output my_gaps.json --threshold 10.0

# Store results in Neo4j
python scripts/detect_gaps.py --store

# Full options
python scripts/detect_gaps.py --output gaps.json --threshold 5.0 --store --verbose
```

### Options

- `--output, -o`: Output JSON file path (default: gaps_{date}.json)
- `--threshold, -t`: Coverage threshold percentage (default: 0.0)
- `--store, -s`: Store gaps in Neo4j database
- `--verbose, -v`: Enable verbose logging

### Scheduled Execution (Cron)

For automated detection, use the provided shell script:

```bash
# Set up as a nightly cron job
30 1 * * * /path/to/testindex/scripts/cron_detect_gaps.sh
```

Edit the script as needed to configure Neo4j credentials and other settings.

## API Usage

You can also use the Gap Detector programmatically:

```python
from testindex.analysis.coverage.gap_detector import GapDetector

# Create detector with optional threshold
detector = GapDetector(coverage_threshold=10.0)

# Find gaps
gaps = detector.find_gaps()
print(f"Found {len(gaps)} gaps")

# Export to JSON
output_file = detector.export_gaps_json("gaps.json")

# Store in Neo4j
stored_count = detector.store_gaps_in_neo4j()
print(f"Stored {stored_count} gaps in Neo4j")
```

## Neo4j Integration

The Gap Detector creates the following Neo4j data:

1. `(:CoverageGap)` nodes for each implementation with coverage below threshold
2. `(:Implementation)-[:HAS_GAP]->(:CoverageGap)` relationships

This data structure can be queried for PR comment bot integration and heat-map visualization. 