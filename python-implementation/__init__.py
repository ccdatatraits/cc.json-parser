"""
JSON Parser - A robust, from-scratch JSON parser implementation in Python.

This package provides:
- JSONParser: Core parsing functionality
- Lexer: Tokenization and lexical analysis
- CLI: Command-line interface for JSON validation and processing

Example usage:
    from json_parser import parse_json, is_valid_json
    
    # Parse JSON string
    data = parse_json('{"name": "John", "age": 30}')
    
    # Validate JSON
    if is_valid_json('{"valid": true}'):
        print("Valid JSON")
"""

__version__ = "1.0.0"
__author__ = "JSON Parser Project"
__email__ = "contact@example.com"

# Import main functions for easy access
from .parser import parse_json, is_valid_json, JSONParser
from .lexer import Lexer, Token, TokenType

__all__ = [
    'parse_json',
    'is_valid_json', 
    'JSONParser',
    'Lexer',
    'Token',
    'TokenType'
]