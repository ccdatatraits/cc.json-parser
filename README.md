# JSON Parser Project

A comprehensive JSON parsing project with implementations in both Python and Rust, featuring robust validation, streaming support, and production-ready CLI tools.

## Project Overview

This project provides two complete JSON parser implementations:

- **Python Implementation**: Full-featured JSON parser with CLI, streaming support, schema validation, and comprehensive testing
- **Rust Implementation**: High-performance streaming JSON parser using iterator patterns with memory-efficient processing

Both implementations are built from scratch without external JSON parsing dependencies, demonstrating fundamental parsing techniques including lexical analysis, recursive descent parsing, and comprehensive error handling.

## Features

### Core Capabilities
- **Complete JSON Support**: All JSON data types (objects, arrays, strings, numbers, booleans, null)
- **Strict RFC 8159 Compliance**: Enforces JSON specification requirements
- **Detailed Error Reporting**: Precise error messages with position information
- **Unicode Support**: Full Unicode handling with proper escape sequences
- **Memory Efficient**: Streaming parsers for large JSON processing

### Advanced Features
- **Multiple Implementations**: Choose between Python (feature-rich) or Rust (performance)
- **CLI Tools**: Production-ready command-line interfaces for both implementations
- **Streaming Support**: Process large JSON files without loading entire content into memory
- **JSON Lines Support**: Parse JSONL format (one JSON object per line)
- **Schema Validation**: Validate JSON against custom schemas (Python)
- **Pretty Printing**: Format JSON output with proper indentation
- **Comprehensive Testing**: Extensive test suites with edge cases, fuzz testing, and benchmarks

## Quick Start

### Python Implementation
```bash
cd python-implementation
python json_parser.py test_file.json
echo '{"name":"John","age":30}' | python json_parser.py --pretty
```

### Rust Implementation
```bash
cd rust-implementation
cargo build --release
echo '{"key": "value"}' | ./target/release/json-cli
```

## Project Structure

```
cc.json-parser/
├── README.md                     # This file - project overview
├── common/                       # Shared test files and resources
│   ├── README.md                # Documentation for test files
│   ├── test-files/              # Standard JSON test cases
│   ├── fuzz-files/              # Fuzz testing invalid JSON samples
│   └── performance-files/       # Performance benchmarking files
├── python-implementation/        # Python JSON parser
│   ├── README.md                # Python-specific documentation
│   ├── json_parser.py           # Main CLI entry point
│   ├── lexer.py                 # Tokenization and lexical analysis
│   ├── parser.py                # Recursive descent parser
│   ├── streaming_parser.py      # Large file streaming support
│   ├── json_validator.py        # Schema validation
│   ├── test_suite.py            # Comprehensive test suite
│   └── setup.py                 # Package installation
└── rust-implementation/          # Rust JSON parser
    ├── README.md                # Rust-specific documentation
    ├── Cargo.toml               # Rust package configuration
    └── src/
        ├── main.rs              # CLI application
        ├── lib.rs               # Library interface
        ├── lexer.rs             # Tokenizer implementation
        ├── parser.rs            # JSON parser logic
        └── types.rs             # Data structures and error types
```

## Implementation Comparison

| Feature | Python | Rust |
|---------|---------|------|
| **JSON Parsing** | ✅ Full support | ✅ Full support |
| **CLI Tool** | ✅ Rich features | ✅ Basic features |
| **Streaming** | ✅ File streaming | ✅ Iterator-based |
| **Schema Validation** | ✅ Yes | ❌ No |
| **Pretty Printing** | ✅ Yes | ✅ Yes |
| **Error Reporting** | ✅ Detailed | ✅ Detailed |
| **Performance** | Good | Excellent |
| **Memory Usage** | Moderate | Low |
| **Dependencies** | Standard library only | minimal (thiserror) |

## Getting Started

### Python Requirements
- Python 3.8 or higher
- No external dependencies (uses Python standard library only)

### Rust Requirements
- Rust 1.70 or higher
- Cargo (included with Rust)

### Installation

#### Python
```bash
cd python-implementation
pip install -e .  # Install as package
# OR
python json_parser.py --help  # Use directly
```

#### Rust
```bash
cd rust-implementation
cargo build --release
cargo install --path .  # Install globally
```

## Usage Examples

### Basic Validation
```bash
# Python
python python-implementation/json_parser.py common/test-files/test_complex.json

# Rust  
./rust-implementation/target/release/json-cli < common/test-files/test_complex.json
```

### Pretty Printing
```bash
# Python
echo '{"compact":"json"}' | python python-implementation/json_parser.py --pretty

# Rust
echo '{"compact":"json"}' | ./rust-implementation/target/release/json-cli --pretty
```

### Streaming Large Files
```bash
# Python streaming parser
python python-implementation/streaming_parser.py large_file.jsonl

# Rust streaming (handles JSONL automatically)
./rust-implementation/target/release/json-cli --stream < large_file.jsonl
```

## Testing

### Python Tests
```bash
cd python-implementation
python -m unittest test_suite.py -v
python test_suite.py --benchmark
```

### Rust Tests
```bash
cd rust-implementation
cargo test
cargo test --release  # Optimized tests
```

### Shared Test Files
Both implementations use the same test files in `common/`:
- `test-files/`: Valid and invalid JSON test cases
- `fuzz-files/`: Generated invalid JSON for robustness testing
- `performance-files/`: Large JSON files for benchmarking

## Performance

### Python Implementation
- Memory: O(n) where n is input size
- Time: O(n) for well-formed JSON
- Benchmark: ~0.09s for typical JSON objects
- Best for: Feature-rich processing, schema validation, development

### Rust Implementation
- Memory: O(1) for streaming, O(n) for full parsing
- Time: O(n) with optimized performance
- Benchmark: ~10x faster than Python implementation
- Best for: High-performance processing, large files, production systems

## Error Handling

Both implementations provide detailed error messages:

```
JSON parsing error: Expected STRING, got RIGHT_BRACE at position 8
JSON parsing error: Trailing comma not allowed at position 15
JSON parsing error: Unterminated string at position 12
JSON parsing error: Invalid number format '123.' at position 10
```

## Contributing

1. Choose the implementation you want to contribute to
2. Fork the repository
3. Create a feature branch: `git checkout -b feature-name`
4. Add tests for new functionality
5. Ensure all tests pass:
   - Python: `python -m unittest test_suite.py`
   - Rust: `cargo test`
6. Submit a pull request

## Development Philosophy

This project demonstrates:
- **Clean Architecture**: Separation of lexing, parsing, and validation concerns
- **Comprehensive Testing**: Edge cases, fuzz testing, and performance benchmarks  
- **Production Quality**: Proper error handling, CLI interfaces, and documentation
- **Educational Value**: Clear, readable implementations for learning parsing techniques
- **Language Comparison**: See the same algorithms implemented in different paradigms

## License

This project is open source and available under the [MIT License](common/LICENSE).

## Support

- Check the implementation-specific README files for detailed usage
- Review test files in `common/` for examples
- See individual implementation directories for architecture details