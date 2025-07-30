# Test Intelligence Engine Query Module

This module provides a structured way to query the knowledge graph and retrieve information about tests and implementations.

## Overview

The Query module enables users to:

1. Create structured queries to find test coverage information
2. Explore relationships between tests, fixtures, and implementations
3. Retrieve information about implementation dependencies and relationships
4. Execute custom Cypher queries for complex scenarios

## Core Components

### Query Models

- `Query`: Base class for all query types
- `TestCoverageQuery`: Find test coverage information for implementations
- `TestRelationshipQuery`: Find relationships between tests and fixtures
- `ImplementationRelationshipQuery`: Find relationships between implementations
- `CustomQuery`: Execute arbitrary Cypher queries

### Query Execution

- `GraphQueryExecutor`: Main executor for graph queries
- `ResultFormatter`: Utilities for formatting and processing query results

## Usage Examples

### Basic Test Coverage Query

```python
from testindex.query import TestCoverageQuery, GraphQueryExecutor
from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.core.config import ConfigModel

# Set up the Neo4j client
config = ConfigModel(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)
client = Neo4jClient(config)

# Create the query executor
executor = GraphQueryExecutor(client)

# Find tests covering a specific implementation
query = TestCoverageQuery(implementation_name="calculate_total")
result = executor.execute(query)

# Access the results
for item in result.data:
    print(f"Test {item['test_name']} covers {item['implementation_name']}")

# Use the formatter for better output
from testindex.query import ResultFormatter
formatted = ResultFormatter.format_coverage_result(result)
print(f"Found {formatted['test_count']} tests covering {formatted['coverage_count']} implementations")
```

### Find Tests Using a Specific Fixture

```python
from testindex.query import TestRelationshipQuery, GraphQueryExecutor

# Create the query executor
executor = GraphQueryExecutor(client)

# Find tests that use a specific fixture
query = TestRelationshipQuery(fixture_name="database_connection")
result = executor.execute(query)

# Format the results
formatted = ResultFormatter.format_test_relationship_result(result)
for test in formatted["tests"]:
    print(f"Test: {test['name']}")
    for fixture in test["fixtures"]:
        print(f"  - Uses fixture: {fixture['name']}")
```

### Find Function Call Relationships

```python
from testindex.query import ImplementationRelationshipQuery, GraphQueryExecutor

# Create the query executor
executor = GraphQueryExecutor(client)

# Find implementations called by a specific function
query = ImplementationRelationshipQuery(
    implementation_name="process_order",
    relationship_type="CALLS"
)
result = executor.execute(query)

# Format the results
formatted = ResultFormatter.format_implementation_relationship_result(result)
for impl in formatted["implementations"]:
    print(f"Function: {impl['name']}")
    for dep in impl["related_implementations"]:
        print(f"  - Calls: {dep['name']}")
```

### Custom Cypher Query

```python
from testindex.query import CustomQuery, GraphQueryExecutor

# Create the query executor
executor = GraphQueryExecutor(client)

# Execute a custom Cypher query
cypher = """
MATCH (t:Test)-[:TESTS]->(i:Implementation)-[:CALLS]->(dep:Implementation)
WHERE t.name = $test_name
RETURN t.name as test_name, i.name as implementation, dep.name as dependency
"""

query = CustomQuery(
    cypher_query=cypher,
    parameters={"test_name": "test_process_order"}
)
result = executor.execute(query)

# Process the results
for item in result.data:
    print(f"Test {item['test_name']} -> Implementation {item['implementation']} -> Dependency {item['dependency']}")
```

## Result Formatting

The `ResultFormatter` class provides utilities for working with query results:

```python
from testindex.query import ResultFormatter

# Convert to dictionary
result_dict = ResultFormatter.to_dict(result)

# Convert to JSON
json_str = ResultFormatter.to_json(result, indent=2)

# Extract specific node types
test_nodes = ResultFormatter.extract_nodes(result, node_type="Test")

# Extract relationships by type
test_relationships = ResultFormatter.extract_relationships(result, relationship_type="TESTS")

# Format coverage results
coverage_info = ResultFormatter.format_coverage_result(result)
```

## Advanced Usage

### Combining Multiple Queries

```python
from testindex.query.utils import merge_query_results

# Execute multiple queries
query1 = TestCoverageQuery(implementation_name="function1")
result1 = executor.execute(query1)

query2 = TestCoverageQuery(implementation_name="function2")
result2 = executor.execute(query2)

# Merge the results
combined_result = merge_query_results([result1, result2])
```

### Getting Query Statistics

```python
from testindex.query.utils import extract_query_stats

# Execute a query
query = TestCoverageQuery(implementation_path="src/module.py")
result = executor.execute(query)

# Get statistics about the result
stats = extract_query_stats(result)
print(f"Results: {stats['result_count']}")
print(f"Nodes: {stats['node_count']}")
print(f"Relationships: {stats['relationship_count']}")
print(f"Node Types: {stats['node_types']}")
```

## Integration with Analysis Pod

The Query module is designed to integrate with the Analysis pod to provide richer insights:

```python
from testindex.query import TestCoverageQuery
from testindex.analysis.coverage import CoverageAnalyzer

# Execute a coverage query
query = TestCoverageQuery(implementation_path="src/module.py")
result = executor.execute(query)

# Use the Analysis pod to analyze coverage
analyzer = CoverageAnalyzer()
coverage_metrics = analyzer.analyze_coverage(result)

print(f"Coverage Percentage: {coverage_metrics.percentage}%")
print(f"Coverage Quality: {coverage_metrics.quality_score}")
``` 