# TestIndex Symbol Extractor

A Python library for extracting code symbols and test symbols from Python files.

## Overview

The Symbol Extractor parses Python files to extract information about classes, functions, methods, and other symbols defined in the code. It can also specifically extract test symbols when used with the TestCodeSymbolExtractor.

## Features

- Extract symbols from Python files and directories
- Extract test symbols from test files
- Support for recursive directory processing
- Configurable error handling
- Extracts module names and test frameworks

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd testindex

# Install the package
pip install -e .
```

## Usage

### Command Line Demo

The repository includes a demo script that showcases the symbol extractor functionality:

```bash
# Extract symbols from a file
python examples/symbol_extractor_demo.py path/to/file.py

# Extract symbols from a directory recursively
python examples/symbol_extractor_demo.py path/to/directory --recursive

# Extract only test symbols
python examples/symbol_extractor_demo.py path/to/directory --tests-only

# Save output to a file
python examples/symbol_extractor_demo.py path/to/file.py --output symbols.json

# Ignore errors during extraction
python examples/symbol_extractor_demo.py path/to/directory --recursive --ignore-errors
```

### Python API

```python
from testindex.core.config import AppConfig
from testindex.preprocessing.parsing.ast_parser import ASTParser
from testindex.preprocessing.parsing.symbol_extractor import SymbolExtractor, TestCodeSymbolExtractor

# Initialize configuration and parser
config = AppConfig()
ast_parser = ASTParser(config)

# Using the base SymbolExtractor
symbol_extractor = SymbolExtractor(config, ast_parser)
symbols = symbol_extractor.extract_symbols_from_file("path/to/your_code.py")

# Using the specialized TestCodeSymbolExtractor (formerly TestSymbolExtractor)
test_extractor = TestCodeSymbolExtractor(config, ast_parser)
test_symbols = test_extractor.extract_test_symbols("path/to/your_test_file.py")

print(f"General symbols: {symbols}")
print(f"Test symbols: {test_symbols}")
```

## Output Format

The symbol extractor produces JSON output that contains detailed information about the extracted symbols. Below is a sample output:

```json
{
  "files": [
    {
      "file_path": "testindex/preprocessing/parsing/symbol_extractor.py",
      "module_name": "testindex.preprocessing.parsing.symbol_extractor",
      "symbols": [
        {
          "name": "SymbolExtractor",
          "type": "class",
          "line_start": 15,
          "line_end": 120,
          "docstring": "Extracts symbols (classes, functions, methods) from Python files.",
          "methods": [
            {
              "name": "__init__",
              "line_start": 18,
              "line_end": 21,
              "docstring": "Initialize the SymbolExtractor with config and AST parser.",
              "parameters": ["self", "config", "ast_parser"]
            },
            {
              "name": "extract_symbols_from_file",
              "line_start": 23,
              "line_end": 45,
              "docstring": "Extract symbols from a single Python file.",
              "parameters": ["self", "file_path", "ignore_errors=False"]
            }
          ]
        }
      ]
    },
    {
      "file_path": "tests/test_example.py",
      "module_name": "tests.test_example",
      "is_test_file": true,
      "test_framework": "pytest",
      "test_symbols": [
        {
          "name": "test_standalone_function",
          "type": "function",
          "line_start": 53,
          "line_end": 60,
          "is_test": true
        }
      ]
    }
  ],
  "summary": {
    "total_files_processed": 2,
    "total_symbols_found": 5,
    "total_test_symbols_found": 3,
    "extraction_timestamp": "2023-07-10T15:30:45.123456"
  }
}
```

Each extracted symbol includes information such as:
- Symbol name and type (class, function, method)
- Line numbers (start and end)
- Docstrings (when available)
- Parameters
- For test files, information about the test framework and test symbols

A complete sample output file is available in the `examples/sample_output.json` file.

## Running Tests

To run the test suite:

```bash
python -m unittest discover tests
```

Or run specific test modules:

```bash
python -m unittest tests.preprocessing.parsing.test_symbol_extractor
```

## License

[Your license information here]