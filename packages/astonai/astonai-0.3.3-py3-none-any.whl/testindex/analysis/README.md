# TestIndex Knowledge: Coverage Map 360

TestIndex Knowledge is a comprehensive test coverage analysis system. The Coverage Map 360 component provides tools for gap detection, PR analysis, and coverage visualization.

## Components

### 1. Gap Detector

The Gap Detector identifies implementations with zero or low test coverage and stores the results in the Knowledge Graph.

Run it with:

```bash
python scripts/detect_gaps.py --threshold 0
```

### 2. Coverage Map API & UI

The Coverage Map API provides a REST interface and web UI for visualizing code coverage gaps detected by the Gap Detector.

Run it with:

```bash
python scripts/run_coverage_api.py
```

Then access the UI at http://localhost:5000

### 3. GitHub PR Comment Bot

The PR Comment Bot analyzes code changes in pull requests and posts comments with coverage information.

Run it with:

```bash
./scripts/run_github_bot.sh
```

See [GitHub PR Bot Documentation](docs/github_pr_bot.md) for more details.

## Getting Started

### Prerequisites

- Python 3.7+
- Neo4j 4.x (or use provided Docker setup)
- Git

### Setup

1. Clone the repository:

```bash
git clone https://github.com/your-org/testindex-knowledge.git
cd testindex-knowledge
```

2. Set up your Python environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Start required services:

```bash
./scripts/start_docker_services.sh
```

4. Run the Gap Detector:

```bash
python scripts/detect_gaps.py
```

5. Start the Coverage Map API:

```bash
python scripts/run_coverage_api.py
```

## Docker Environment

For convenience, you can use Docker to run the required services:

```bash
./scripts/start_docker_services.sh
```

This will start Neo4j and other required services.

## Testing

Run tests with:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 