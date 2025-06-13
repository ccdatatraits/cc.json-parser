from typing import Any, Dict, List, Union
from lexer import Lexer, Token, TokenType

class JSONParser:
    def __init__(self, token_list: List[Token]):
        self.tokens = token_list
        self.current_token_index = 0
    
    def peek(self) -> Token:
        if self.current_token_index >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current_token_index]
    
    def advance(self) -> Token:
        if self.current_token_index < len(self.tokens):
            current_token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return current_token
        return self.tokens[-1]  # EOF token
    
    def expect(self, expected_token_type: TokenType) -> Token:
        actual_token = self.advance()
        if actual_token.type != expected_token_type:
            raise ValueError(f"Expected {expected_token_type.value}, got {actual_token.type.value} at position {actual_token.position}")
        return actual_token
    
    def parse_value(self) -> Any:
        current_token = self.peek()
        
        if current_token.type == TokenType.LEFT_BRACE:
            return self.parse_object()
        elif current_token.type == TokenType.LEFT_BRACKET:
            return self.parse_array()
        elif current_token.type == TokenType.STRING:
            self.advance()
            return current_token.value
        elif current_token.type == TokenType.NUMBER:
            self.advance()
            # Try to parse as int first, then float
            try:
                if '.' in current_token.value or 'e' in current_token.value.lower():
                    return float(current_token.value)
                else:
                    return int(current_token.value)
            except ValueError:
                raise ValueError(f"Invalid number format '{current_token.value}' at position {current_token.position}")
        elif current_token.type == TokenType.BOOLEAN:
            self.advance()
            return current_token.value == 'true'
        elif current_token.type == TokenType.NULL:
            self.advance()
            return None
        else:
            raise ValueError(f"Unexpected token {current_token.type.value} at position {current_token.position}")
    
    def parse_object(self) -> Dict[str, Any]:
        self.expect(TokenType.LEFT_BRACE)
        
        json_object = {}
        
        # Handle empty object
        if self.peek().type == TokenType.RIGHT_BRACE:
            self.advance()
            return json_object
        
        while True:
            # Parse key (must be string)
            key_token = self.expect(TokenType.STRING)
            object_key = key_token.value
            
            # Expect colon
            self.expect(TokenType.COLON)
            
            # Parse value
            object_value = self.parse_value()
            json_object[object_key] = object_value
            
            # Check for continuation
            separator_token = self.peek()
            if separator_token.type == TokenType.RIGHT_BRACE:
                break
            elif separator_token.type == TokenType.COMMA:
                self.advance()  # consume comma
                # After comma, we must have another key-value pair
                if self.peek().type == TokenType.RIGHT_BRACE:
                    raise ValueError(f"Trailing comma not allowed at position {self.peek().position}")
            else:
                raise ValueError(f"Expected ',' or '}}' but got {separator_token.type.value} at position {separator_token.position}")
        
        self.expect(TokenType.RIGHT_BRACE)
        return json_object
    
    def parse_array(self) -> List[Any]:
        self.expect(TokenType.LEFT_BRACKET)
        
        json_array = []
        
        # Handle empty array
        if self.peek().type == TokenType.RIGHT_BRACKET:
            self.advance()
            return json_array
        
        while True:
            # Parse value
            array_element = self.parse_value()
            json_array.append(array_element)
            
            # Check for continuation
            separator_token = self.peek()
            if separator_token.type == TokenType.RIGHT_BRACKET:
                break
            elif separator_token.type == TokenType.COMMA:
                self.advance()  # consume comma
                # After comma, we must have another value
                if self.peek().type == TokenType.RIGHT_BRACKET:
                    raise ValueError(f"Trailing comma not allowed at position {self.peek().position}")
            else:
                raise ValueError(f"Expected ',' or ']' but got {separator_token.type.value} at position {separator_token.position}")
        
        self.expect(TokenType.RIGHT_BRACKET)
        return json_array
    
    def parse(self) -> Any:
        if not self.tokens or self.tokens[0].type == TokenType.EOF:
            raise ValueError("Empty input")
        
        parsed_json_value = self.parse_value()
        
        # Ensure we've consumed all tokens except EOF
        if self.peek().type != TokenType.EOF:
            raise ValueError(f"Unexpected token after JSON value: {self.peek().type.value} at position {self.peek().position}")
        
        return parsed_json_value

def parse_json(json_text: str) -> Any:
    try:
        json_lexer = Lexer(json_text)
        token_list = json_lexer.tokenize()
        json_parser = JSONParser(token_list)
        return json_parser.parse()
    except Exception as parsing_error:
        raise ValueError(f"JSON parsing error: {str(parsing_error)}")

def is_valid_json(json_text: str) -> bool:
    try:
        parse_json(json_text)
        return True
    except:
        return False