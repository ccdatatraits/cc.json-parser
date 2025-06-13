import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE" 
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    COMMA = "COMMA"
    COLON = "COLON"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    position: int

class Lexer:
    def __init__(self, input_text: str):
        self.input_text = input_text
        self.current_position = 0
        self.current_char = self.input_text[self.current_position] if self.current_position < len(self.input_text) else None
    
    def advance(self):
        self.current_position += 1
        if self.current_position >= len(self.input_text):
            self.current_char = None
        else:
            self.current_char = self.input_text[self.current_position]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def read_string(self) -> str:
        if self.current_char != '"':
            raise ValueError(f"Expected '\"' at position {self.current_position}")
        
        self.advance()  # skip opening quote
        string_content = ""
        
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    raise ValueError("Unterminated string escape")
                
                escape_char_mappings = {
                    '"': '"',
                    '\\': '\\',
                    '/': '/',
                    'b': '\b',
                    'f': '\f',
                    'n': '\n',
                    'r': '\r',
                    't': '\t'
                }
                
                if self.current_char in escape_char_mappings:
                    string_content += escape_char_mappings[self.current_char]
                elif self.current_char == 'u':
                    # Unicode escape sequence
                    self.advance()
                    unicode_hex_digits = ""
                    for _ in range(4):
                        if self.current_char is None or not self.current_char.isdigit() and self.current_char.lower() not in 'abcdef':
                            raise ValueError("Invalid unicode escape sequence")
                        unicode_hex_digits += self.current_char
                        self.advance()
                    string_content += chr(int(unicode_hex_digits, 16))
                    continue
                else:
                    raise ValueError(f"Invalid escape character '\\{self.current_char}'")
            else:
                string_content += self.current_char
            self.advance()
        
        if self.current_char != '"':
            raise ValueError("Unterminated string")
        
        self.advance()  # skip closing quote
        return string_content
    
    def read_number(self) -> str:
        number_string = ""
        
        # Handle negative numbers
        if self.current_char == '-':
            number_string += self.current_char
            self.advance()
        
        # Must have at least one digit
        if self.current_char is None or not self.current_char.isdigit():
            raise ValueError("Invalid number format")
        
        # Handle integer part
        if self.current_char == '0':
            number_string += self.current_char
            self.advance()
        else:
            while self.current_char is not None and self.current_char.isdigit():
                number_string += self.current_char
                self.advance()
        
        # Handle decimal part
        if self.current_char == '.':
            number_string += self.current_char
            self.advance()
            
            if self.current_char is None or not self.current_char.isdigit():
                raise ValueError("Invalid number format: decimal point must be followed by digits")
            
            while self.current_char is not None and self.current_char.isdigit():
                number_string += self.current_char
                self.advance()
        
        # Handle exponent part
        if self.current_char and self.current_char.lower() == 'e':
            number_string += self.current_char
            self.advance()
            
            if self.current_char in ['+', '-']:
                number_string += self.current_char
                self.advance()
            
            if self.current_char is None or not self.current_char.isdigit():
                raise ValueError("Invalid number format: exponent must have digits")
            
            while self.current_char is not None and self.current_char.isdigit():
                number_string += self.current_char
                self.advance()
        
        return number_string
    
    def read_literal(self) -> str:
        literal_value = ""
        while (self.current_char is not None and 
               self.current_char.isalpha()):
            literal_value += self.current_char
            self.advance()
        return literal_value
    
    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            token_start_position = self.current_position
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LEFT_BRACE, '{', token_start_position)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RIGHT_BRACE, '}', token_start_position)
            
            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LEFT_BRACKET, '[', token_start_position)
            
            if self.current_char == ']':
                self.advance()
                return Token(TokenType.RIGHT_BRACKET, ']', token_start_position)
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', token_start_position)
            
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':', token_start_position)
            
            if self.current_char == '"':
                string_value = self.read_string()
                return Token(TokenType.STRING, string_value, token_start_position)
            
            if self.current_char.isdigit() or self.current_char == '-':
                number_value = self.read_number()
                return Token(TokenType.NUMBER, number_value, token_start_position)
            
            if self.current_char.isalpha():
                literal_value = self.read_literal()
                if literal_value == 'true' or literal_value == 'false':
                    return Token(TokenType.BOOLEAN, literal_value, token_start_position)
                elif literal_value == 'null':
                    return Token(TokenType.NULL, literal_value, token_start_position)
                else:
                    raise ValueError(f"Invalid literal '{literal_value}' at position {token_start_position}")
            
            raise ValueError(f"Unexpected character '{self.current_char}' at position {self.current_position}")
        
        return Token(TokenType.EOF, '', self.current_position)
    
    def tokenize(self) -> List[Token]:
        token_list = []
        current_token = self.get_next_token()
        
        while current_token.type != TokenType.EOF:
            token_list.append(current_token)
            current_token = self.get_next_token()
        
        token_list.append(current_token)  # Add EOF token
        return token_list