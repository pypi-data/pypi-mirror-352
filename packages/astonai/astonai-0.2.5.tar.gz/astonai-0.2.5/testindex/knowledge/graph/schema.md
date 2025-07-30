# Knowledge Graph Schema Documentation

This document describes the schema used by the knowledge graph module for representing code structure, relationships, and metadata.

## Node Types

### Module

Represents a Python module file.

**Properties:**
- `name`: The module name
- `file_path`: The absolute file path
- `is_package`: Boolean indicating if the module is a package
- `docstring`: The module's docstring if available
- `imports`: List of imports in the module
- `last_modified`: Timestamp of last modification

### Class

Represents a Python class definition.

**Properties:**
- `name`: The class name
- `file_path`: The absolute file path
- `module`: The module containing this class
- `docstring`: The class's docstring if available
- `bases`: List of base classes (for inheritance)
- `is_abstract`: Boolean indicating if the class is abstract
- `line_number`: Starting line number in the file
- `end_line_number`: Ending line number in the file

### Function

Represents a standalone Python function.

**Properties:**
- `name`: The function name
- `file_path`: The absolute file path
- `module`: The module containing this function
- `docstring`: The function's docstring if available
- `parameters`: List of parameter names
- `return_type`: The return type if type hints are used
- `is_async`: Boolean indicating if the function is asynchronous
- `line_number`: Starting line number in the file
- `end_line_number`: Ending line number in the file

### Method

Represents a Python class method.

**Properties:**
- `name`: The method name
- `class_name`: The name of the class containing this method
- `file_path`: The absolute file path
- `module`: The module containing this method
- `docstring`: The method's docstring if available
- `parameters`: List of parameter names
- `return_type`: The return type if type hints are used
- `is_async`: Boolean indicating if the method is asynchronous
- `is_static`: Boolean indicating if the method is static
- `is_class_method`: Boolean indicating if the method is a class method
- `is_property`: Boolean indicating if the method is a property
- `line_number`: Starting line number in the file
- `end_line_number`: Ending line number in the file

### TestClass

Represents a test class (e.g., pytest or unittest).

**Properties:**
- `name`: The test class name
- `file_path`: The absolute file path
- `module`: The module containing this test class
- `framework`: The testing framework used (e.g., 'pytest', 'unittest')
- `tests_implementation`: The name of the implementation class being tested
- `line_number`: Starting line number in the file
- `end_line_number`: Ending line number in the file

### TestFunction

Represents a test function or method.

**Properties:**
- `name`: The test function/method name
- `file_path`: The absolute file path
- `module`: The module containing this test
- `class_name`: The test class name (if part of a test class)
- `tests_implementation`: The name of the implementation being tested
- `framework`: The testing framework used
- `line_number`: Starting line number in the file
- `end_line_number`: Ending line number in the file

## Relationship Types

### IMPORTS

Represents an import relationship between modules.

**Properties:**
- `source`: The importing module
- `target`: The imported module
- `import_type`: Type of import ('import' or 'from')
- `alias`: Alias used for the import if any

### CONTAINS

Represents a containment relationship between a module and its classes/functions or a class and its methods.

**Properties:**
- `source`: The container (module or class)
- `target`: The contained entity (class, function, or method)
- `visibility`: Visibility ('public', 'protected', or 'private')

### CALLS

Represents a function/method call relationship.

**Properties:**
- `source`: The calling function/method
- `target`: The called function/method
- `call_count`: Number of calls within the source
- `line_numbers`: List of line numbers where calls occur

### INHERITS_FROM

Represents a class inheritance relationship.

**Properties:**
- `source`: The child class
- `target`: The parent class
- `is_direct`: Boolean indicating if it's direct inheritance

### TESTS

Represents a testing relationship between a test and an implementation.

**Properties:**
- `source`: The test function/method/class
- `target`: The implementation being tested
- `confidence`: Confidence score (0.0-1.0) of this relationship
- `detection_method`: Method used to detect this relationship (e.g., 'static_analysis', 'naming_convention')

### USES

Represents usage of a variable, parameter, or attribute.

**Properties:**
- `source`: The function/method using the variable
- `target`: The variable, parameter, or attribute being used
- `usage_type`: Type of usage ('read', 'write', or 'read_write')
- `line_numbers`: List of line numbers where usage occurs

## Schema Version

The schema follows semantic versioning. The current version is 1.0.0.

**Version History:**
- 1.0.0: Initial schema definition

## Neo4j Constraints

The following Neo4j constraints are applied to ensure data integrity:

1. Unique node IDs for all node types
2. Unique combination of name and file_path for modules, classes, and functions
3. Unique combination of class_name, name, and file_path for methods

## Usage Notes

1. All file paths should be stored as absolute paths for consistency
2. Line numbers are 1-indexed (matching Python's line numbering)
3. For relationships that can be derived (like CALLS), the confidence property can be used to indicate certainty
4. The schema supports both static and dynamic analysis results 