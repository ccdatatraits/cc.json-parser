# Python JSON Parser Implementation

A comprehensive, production-ready JSON parser built from scratch in Python with extensive features including CLI tools, streaming support, schema validation, and comprehensive testing.

## Features

### Core JSON Processing
- **Complete JSON Support**: All JSON data types (objects, arrays, strings, numbers, booleans, null)
- **Strict RFC 8159 Compliance**: Enforces JSON specification requirements
- **Detailed Error Reporting**: Precise error messages with character position information
- **Unicode Support**: Full Unicode handling with proper escape sequence processing
- **Type Safety**: Proper Python type conversion with validation

### Advanced Features
- **Streaming Parser**: Memory-efficient parsing of large JSON files via `streaming_parser.py`
- **JSON Lines Support**: Parse JSONL format (one JSON object per line)
- **Schema Validation**: Validate JSON against custom schemas with type checking via `json_validator.py`
- **Pretty Printing**: Format JSON output with configurable indentation
- **Multiple Encodings**: Support for various text encodings (UTF-8, UTF-16, etc.)

### Production-Ready CLI
- **Rich Command Line Interface**: Comprehensive CLI with multiple options and flags
- **Flexible Input/Output**: Read from files, stdin, URLs; write to files or stdout
- **Debug and Logging**: Built-in logging levels and debug modes
- **Validation-Only Mode**: Validate without outputting parsed JSON
- **Quiet Mode**: Suppress output for scripting and automation
- **Performance Monitoring**: Built-in timing and profiling options

## Architecture

The parser follows a clean, modular architecture:

```
python-implementation/
├── json_parser.py         # Main CLI entry point and argument parsing
├── lexer.py              # Tokenization and lexical analysis
├── parser.py             # Recursive descent parser implementation  
├── streaming_parser.py   # Large file streaming support
├── json_validator.py     # Schema validation and type checking
├── test_suite.py         # Comprehensive test suite with benchmarks
├── setup.py              # Package installation and distribution
└── __init__.py           # Package initialization and version
```

### Component Details

#### `lexer.py` - Lexical Analysis
- **Tokenizer**: Breaks JSON input into tokens (strings, numbers, operators, etc.)
- **Error Detection**: Identifies invalid characters and malformed tokens
- **Position Tracking**: Maintains precise character positions for error reporting
- **Unicode Handling**: Proper Unicode escape sequence processing

#### `parser.py` - Recursive Descent Parser
- **Grammar Implementation**: Implements JSON grammar rules recursively
- **Type Conversion**: Converts tokens to appropriate Python types
- **Validation**: Enforces JSON specification compliance
- **Error Recovery**: Provides meaningful error messages with context

#### `streaming_parser.py` - Large File Support
- **Memory Efficient**: Processes large files without loading entire content
- **Iterator Pattern**: Yields parsed objects one at a time
- **JSON Lines**: Supports JSONL format for structured data streams
- **Error Resilience**: Continues processing on individual object errors

#### `json_validator.py` - Schema Validation
- **Type Checking**: Validates JSON structure against schemas
- **Custom Rules**: Extensible validation rule system
- **Detailed Reports**: Comprehensive validation error reporting
- **Performance Optimized**: Efficient validation algorithms

## Installation

### Requirements
- Python 3.8 or higher
- No external dependencies (uses Python standard library only)

### Setup Options

#### Option 1: Direct Usage (Recommended for testing)
```bash
# No installation needed - ready to use!
python json_parser.py --help
python json_parser.py test_file.json
```

#### Option 2: Package Installation
```bash
# Install as development package
pip install -e .

# Use installed commands
json-parser test_file.json
jsonparse --pretty < data.json
```

#### Option 3: System-wide Installation
```bash
# Install from source
python setup.py install

# Or via pip if published
pip install json-parser
```

## Usage

### Command Line Interface

#### Basic Validation
```bash
# Validate a specific file
python json_parser.py filename.json

# Validate from stdin
cat data.json | python json_parser.py
echo '{"valid": true}' | python json_parser.py

# Check exit codes for automation
python json_parser.py valid.json && echo "Valid JSON"
python json_parser.py invalid.json || echo "Invalid JSON"
```

#### Advanced CLI Options
```bash
# Pretty print JSON with indentation
python json_parser.py --pretty input.json

# Validation-only mode (no output)
python json_parser.py --validate-only large_file.json

# Debug mode with detailed logging
python json_parser.py --debug --output formatted.json input.json

# Quiet mode for scripting
python json_parser.py --quiet --validate-only data.json || exit 1

# Custom output file and encoding
python json_parser.py --output result.json --encoding utf-16 input.json
```

#### Streaming Large Files
```bash
# Stream large JSON files
python streaming_parser.py large_file.json

# Process JSON Lines format
python streaming_parser.py --jsonl data.jsonl

# Stream with validation
python streaming_parser.py --validate-schema schema.json data.json
```

### Python API

#### Basic Parsing
```python
from parser import parse_json, is_valid_json

# Parse JSON string to Python object
try:
    data = parse_json('{"name": "John", "age": 30}')
    print(data)  # {'name': 'John', 'age': 30}
except ValueError as e:
    print(f"Invalid JSON: {e}")

# Check validity without parsing
if is_valid_json('{"valid": true}'):
    print("Valid JSON")
```

#### Advanced Usage
```python
from streaming_parser import StreamingJSONParser
from json_validator import JSONValidator

# Stream large files
parser = StreamingJSONParser('large_file.json')
for obj in parser:
    process_object(obj)

# Schema validation
validator = JSONValidator(schema_file='schema.json')
if validator.validate(json_data):
    print("Valid according to schema")
else:
    print("Validation errors:", validator.errors)
```

## CLI Reference

```
usage: json_parser.py [-h] [--pretty] [--validate-only] [--quiet] [--debug]
                      [--output OUTPUT] [--encoding ENCODING] [--version]
                      [file]

JSON Parser - validates and processes JSON input

positional arguments:
  file                  JSON file to parse (if not provided, reads from stdin)

optional arguments:
  -h, --help            show this help message and exit
  --pretty, -p          Pretty print the JSON output
  --validate-only, -v   Only validate, do not output parsed JSON
  --quiet, -q           Suppress error messages
  --debug, -d           Enable debug output
  --output OUTPUT, -o OUTPUT
                        Output file (default: stdout)
  --encoding ENCODING   Input file encoding (default: utf-8)
  --version             show program version number and exit
```

### Exit Codes
- `0`: Valid JSON
- `1`: Invalid JSON, file not found, or other error
- `130`: Operation cancelled by user (Ctrl+C)

## Testing

### Run Test Suite
```bash
# Run all tests with verbose output
python -m unittest test_suite.py -v

# Quick test run
python test_suite.py

# Run specific test categories
python test_suite.py --valid-only     # Only valid JSON tests
python test_suite.py --invalid-only   # Only invalid JSON tests
python test_suite.py --edge-cases     # Edge case tests
```

### Performance Benchmarking
```bash
# Run performance benchmarks
python test_suite.py --benchmark

# Custom benchmark parameters
python test_suite.py --benchmark --iterations 1000 --size large
```

### Test Categories

1. **Valid JSON Tests**: Ensure properly formatted JSON parses correctly
2. **Invalid JSON Tests**: Verify malformed JSON is properly rejected
3. **Edge Cases**: Unicode, scientific notation, deeply nested structures
4. **Fuzz Tests**: Random invalid JSON generation for robustness
5. **Performance Tests**: Large objects, arrays, and deeply nested structures
6. **Streaming Tests**: Large file processing and memory usage
7. **Schema Validation Tests**: Custom schema validation scenarios

### Sample Test Output
```
==================================================
JSON Parser Test Suite
==================================================
test_valid_empty_object (__main__.TestValidJSON) ... ok
test_valid_simple_string (__main__.TestValidJSON) ... ok
test_invalid_trailing_comma (__main__.TestInvalidJSON) ... ok
test_performance_large_array (__main__.TestPerformance) ... ok

==================================================
Performance Benchmark Results
==================================================
empty_object         | Avg: 0.0882s | Min: 0.0850s | Max: 0.0900s
simple_string        | Avg: 0.0919s | Min: 0.0870s | Max: 0.1015s
medium_object        | Avg: 0.0916s | Min: 0.0876s | Max: 0.0991s
large_array          | Avg: 0.1250s | Min: 0.1200s | Max: 0.1350s

Ran 47 tests in 2.341s
OK
```

## Supported JSON Features

### ✅ Fully Supported
- **Objects**: `{"key": "value"}` with proper key-value pairs
- **Arrays**: `[1, 2, 3]` with mixed types
- **Strings**: `"hello world"` with escape sequences (`\"`, `\\`, `\n`, `\t`, `\r`, `\b`, `\f`)
- **Numbers**: 
  - Integers: `123`, `-456`
  - Floats: `12.34`, `-56.78`
  - Scientific notation: `1.23e10`, `4.56E-7`
- **Booleans**: `true`, `false`
- **Null**: `null`
- **Unicode**: `"Hello \u4e16\u754c"` (proper Unicode escape sequences)
- **Nested structures**: Arbitrary depth nesting

### ❌ Correctly Rejected (JSON Spec Compliance)
- **Trailing commas**: `{"key": "value",}`, `[1, 2, 3,]`
- **Unquoted keys**: `{key: "value"}`
- **Single quotes**: `{'key': 'value'}`
- **Comments**: `{"key": /* comment */ "value"}`
- **Undefined values**: `undefined`
- **Function calls**: `new Date()`
- **Leading zeros**: `01234`
- **Hex numbers**: `0xFF`

## Error Messages

The parser provides detailed, actionable error messages:

```python
# Missing value error
"JSON parsing error: Expected value after ':' at position 8"

# Trailing comma error  
"JSON parsing error: Trailing comma not allowed in object at position 15"

# Unterminated string error
"JSON parsing error: Unterminated string starting at position 5"

# Invalid number format
"JSON parsing error: Invalid number format '123.' at position 10"

# Unicode escape error
"JSON parsing error: Invalid Unicode escape sequence '\\u123' at position 12"
```

## Performance Characteristics

- **Time Complexity**: O(n) where n is input size
- **Space Complexity**: O(n) for parsed data structure, O(d) for parser stack where d is nesting depth
- **Memory Usage**: ~2-3x input size for typical JSON (varies by structure)
- **Streaming**: O(1) memory usage for streaming parser
- **Benchmarks**: 
  - Small JSON (< 1KB): ~0.001s
  - Medium JSON (10-100KB): ~0.01-0.1s  
  - Large JSON (1-10MB): ~0.1-1.0s

## Development

### Adding New Features

1. **Extend Grammar**: Modify `parser.py` for new JSON constructs
2. **Add Tokens**: Update `lexer.py` for new token types
3. **Update CLI**: Enhance `json_parser.py` for new command-line options
4. **Add Tests**: Include test cases in `test_suite.py`

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Document functions with docstrings
- Maintain test coverage above 90%

### Testing New Changes
```bash
# Run full test suite
python -m unittest test_suite.py -v

# Check performance impact
python test_suite.py --benchmark

# Test edge cases
python test_suite.py --fuzz --iterations 10000
```

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'parser'"
```bash
# Ensure you're in the python-implementation directory
cd python-implementation
python json_parser.py
```

#### "UnicodeDecodeError" with input files
```bash
# Specify encoding explicitly
python json_parser.py --encoding utf-16 input.json
```

#### Large file memory issues
```bash
# Use streaming parser for large files
python streaming_parser.py large_file.json
```

#### Performance issues
```bash
# Enable debug mode to identify bottlenecks
python json_parser.py --debug large_file.json
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes following the code style guidelines
4. Add comprehensive tests for new functionality
5. Ensure all tests pass: `python -m unittest test_suite.py`
6. Update documentation as needed
7. Submit a pull request

## License

This implementation is part of the JSON Parser project and is available under the [MIT License](../common/LICENSE).