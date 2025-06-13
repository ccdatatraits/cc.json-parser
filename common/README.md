# JSON Parser

A robust, from-scratch JSON parser implementation in Python that validates JSON according to the official [JSON specification](https://www.json.org/). This project demonstrates fundamental parsing techniques including lexical analysis, recursive descent parsing, and comprehensive error handling.

## Features

### Core JSON Processing
- **Complete JSON Support**: Handles all JSON data types (objects, arrays, strings, numbers, booleans, null)
- **Strict Validation**: Enforces JSON specification compliance (no trailing commas, proper escaping, etc.)
- **Detailed Error Reporting**: Provides precise error messages with position information
- **Unicode Support**: Full Unicode handling with proper escape sequence processing

### Advanced Features
- **Streaming Parser**: Memory-efficient parsing of large JSON files
- **JSON Lines Support**: Parse JSONL format (one JSON object per line)
- **Schema Validation**: Validate JSON against custom schemas with type checking
- **Pretty Printing**: Format JSON output with proper indentation
- **Multiple Encodings**: Support for various text encodings

### Production-Ready CLI
- **Rich Command Line Interface**: Comprehensive CLI with multiple options
- **Flexible Input/Output**: Read from files or stdin, write to files or stdout
- **Debug and Logging**: Built-in logging and debug modes
- **Validation-Only Mode**: Validate without outputting parsed JSON
- **Quiet Mode**: Suppress error messages for scripting

### Developer Experience
- **Comprehensive Testing**: 25+ test cases including edge cases, fuzz testing, and performance benchmarks
- **Clean Architecture**: Separate lexer and parser components with clear separation of concerns
- **Package Distribution**: Proper Python package with setup.py for easy installation
- **API Documentation**: Both CLI and programmatic interfaces

## Quick Start

### Basic validation:
```bash
python json_parser.py test_step1.json
echo $?  # 0 for valid JSON, 1 for invalid
```

### Pretty print JSON:
```bash
echo '{"name":"John","age":30}' | python json_parser.py --pretty
```

### Validation-only mode:
```bash
python json_parser.py --validate-only large_file.json && echo "Valid!"
```

### Advanced usage:
```bash
# Debug mode with output to file
python json_parser.py --debug --output formatted.json --pretty input.json

# Quiet mode for scripting
python json_parser.py --quiet --validate-only data.json || exit 1
```

### Run tests and benchmarks:
```bash
python -m unittest test_suite.py -v          # Run test suite
python test_suite.py --benchmark             # Performance benchmarks
```

## Installation

### Prerequisites
- Python 3.8 or higher
- No external dependencies required (uses only Python standard library)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd json-parser

# No installation needed - ready to use!
python json_parser.py --help
```

## Usage

### Command Line Interface

The JSON parser accepts input from either a file or stdin:

```bash
# Validate a specific file
python json_parser.py filename.json

# Validate from stdin
cat data.json | python json_parser.py
echo '{"valid": true}' | python json_parser.py

# Check exit codes
python json_parser.py valid.json && echo "Valid JSON"
python json_parser.py invalid.json || echo "Invalid JSON"
```

### Exit Codes
- `0`: Valid JSON
- `1`: Invalid JSON or file not found

### Python API

You can also use the parser programmatically:

```python
from parser import parse_json, is_valid_json

# Parse JSON and get Python object
try:
    data = parse_json('{"name": "John", "age": 30}')
    print(data)  # {'name': 'John', 'age': 30}
except ValueError as e:
    print(f"Invalid JSON: {e}")

# Just check if JSON is valid
if is_valid_json('{"valid": true}'):
    print("Valid JSON")
```

## Project Structure

```
json-parser/
├── README.md                    # Project documentation
├── LICENSE                     # MIT license
├── setup.py                    # Package installation script
├── MANIFEST.in                 # Package distribution manifest
├── __init__.py                 # Package initialization
├── json_parser.py              # Main CLI entry point
├── lexer.py                    # Tokenization and lexical analysis
├── parser.py                   # Recursive descent parser
├── streaming_parser.py         # Large file streaming support
├── json_validator.py           # Schema validation
├── test_suite.py               # Comprehensive test suite
├── test_config.json            # Configurable test cases
├── test_step*.json             # Basic test files
├── test_complex.json           # Complex nested JSON test
└── test_invalid.json           # Invalid JSON test case
```

## Architecture

The parser follows a traditional two-phase approach:

### 1. Lexical Analysis (`lexer.py`)
- **Tokenizer**: Breaks input into tokens (strings, numbers, operators, etc.)
- **Error Detection**: Identifies invalid characters and malformed tokens
- **Position Tracking**: Maintains character positions for error reporting

### 2. Parsing (`parser.py`)
- **Recursive Descent Parser**: Implements JSON grammar rules
- **Type Conversion**: Converts tokens to appropriate Python types
- **Validation**: Enforces JSON specification compliance
- **Error Recovery**: Provides meaningful error messages

### 3. Testing (`test_suite.py`)
- **Unit Tests**: Validates parser functionality with unittest framework
- **Fuzz Testing**: Generates random invalid JSON for robustness testing
- **Performance Tests**: Benchmarks parsing speed with large datasets
- **Configuration-Driven**: Test cases defined in `test_config.json` for easy maintenance

## Testing

### Run All Tests
```bash
# Verbose test output
python -m unittest test_suite.py -v

# Quick test run
python test_suite.py
```

### Test Categories

1. **Valid JSON Tests**: Ensure properly formatted JSON parses correctly
2. **Invalid JSON Tests**: Verify malformed JSON is rejected
3. **Edge Cases**: Unicode, scientific notation, deeply nested structures
4. **Fuzz Tests**: Random invalid JSON generation for robustness
5. **Performance Tests**: Large objects, arrays, and deeply nested structures

### Performance Benchmarking
```bash
python test_suite.py --benchmark
```

Sample benchmark output:
```
==================================================
JSON Parser Performance Benchmark
==================================================
empty_object         | Avg: 0.0882s | Min: 0.0850s | Max: 0.0900s
simple_string        | Avg: 0.0919s | Min: 0.0870s | Max: 0.1015s
medium_object        | Avg: 0.0916s | Min: 0.0876s | Max: 0.0991s
```

### Adding New Tests

Tests are configured in `test_config.json`:

```json
{
  "edge_case_tests": [
    {
      "name": "your_test_name",
      "content": "your JSON content",
      "file": "your_test_file.json",
      "description": "Test description",
      "should_pass": true
    }
  ]
}
```

## Supported JSON Features

### ✅ Fully Supported
- Objects: `{"key": "value"}`
- Arrays: `[1, 2, 3]`
- Strings: `"hello world"` with escape sequences
- Numbers: `123`, `-45.67`, `1.23e-10`
- Booleans: `true`, `false`
- Null: `null`
- Unicode: `"Hello \u4e16\u754c"`
- Nested structures of any depth

### ❌ Correctly Rejected
- Trailing commas: `{"key": "value",}`
- Unquoted keys: `{key: "value"}`
- Single quotes: `{'key': 'value'}`
- Comments: `{"key": /* comment */ "value"}`
- Undefined: `undefined`

## Examples

### Valid JSON Examples
```json
{}
{"name": "John", "age": 30}
[1, 2, 3, true, false, null]
{
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ],
  "count": 2
}
```

### Invalid JSON Examples
```json
{"key": }                    // Missing value
{"key" "value"}              // Missing colon
{"key": "value",}            // Trailing comma
[1, 2, 3,]                   // Trailing comma in array
{"key": "unterminated string // Unterminated string
{key: "value"}               // Unquoted key
```

## Error Messages

The parser provides detailed error messages with position information:

```
JSON parsing error: Expected STRING, got RIGHT_BRACE at position 8
JSON parsing error: Trailing comma not allowed at position 15
JSON parsing error: Unterminated string
JSON parsing error: Invalid number format '123.' at position 10
```

## Performance Characteristics

- **Memory**: O(n) where n is input size
- **Time**: O(n) for well-formed JSON
- **Scalability**: Handles JSON files up to available memory
- **Benchmarks**: Parses typical JSON objects in ~0.09 seconds

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Add tests for new functionality in `test_config.json`
4. Ensure all tests pass: `python -m unittest test_suite.py`
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Development Notes

This parser was built as a coding challenge solution, demonstrating:
- Clean, readable code with meaningful variable names
- Comprehensive error handling and reporting
- Extensive testing including edge cases and performance
- Proper separation of concerns (lexer vs parser)
- Configuration-driven testing for maintainability

The implementation prioritizes correctness and clarity over raw performance, making it suitable for educational purposes and moderate-scale JSON processing tasks.