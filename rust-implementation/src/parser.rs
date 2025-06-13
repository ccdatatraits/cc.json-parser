use std::collections::HashMap;
use std::io::Read;
use crate::types::{Token, TokenType, JsonValue, ParseError, ParseResult};
use crate::lexer::Lexer;

pub struct StreamingJsonParser<R: Read> {
    lexer: Lexer<R>,
    current_token: Option<Token>,
    peeked_token: Option<ParseResult<Token>>,
}

impl<R: Read> StreamingJsonParser<R> {
    pub fn new(reader: R) -> Self {
        Self {
            lexer: Lexer::new(reader),
            current_token: None,
            peeked_token: None,
        }
    }

    fn peek_token(&mut self) -> &ParseResult<Token> {
        if self.peeked_token.is_none() {
            self.peeked_token = Some(
                self.lexer.next()
                    .unwrap_or_else(|| Ok(Token::new(TokenType::Eof, 0)))
            );
        }
        self.peeked_token.as_ref().unwrap()
    }

    fn advance_token(&mut self) -> ParseResult<Token> {
        if let Some(peeked) = self.peeked_token.take() {
            let token = peeked?;
            self.current_token = Some(token.clone());
            Ok(token)
        } else {
            let token = self.lexer.next()
                .unwrap_or_else(|| Ok(Token::new(TokenType::Eof, 0)))?;
            self.current_token = Some(token.clone());
            Ok(token)
        }
    }

    fn expect_token(&mut self, expected: TokenType) -> ParseResult<Token> {
        let token = self.advance_token()?;
        if std::mem::discriminant(&token.token_type) != std::mem::discriminant(&expected) {
            return Err(ParseError::UnexpectedToken {
                expected: format!("{:?}", expected),
                found: format!("{:?}", token.token_type),
                position: token.position,
            });
        }
        Ok(token)
    }

    fn parse_value(&mut self) -> ParseResult<JsonValue> {
        let token = match self.peek_token() {
            Ok(token) => token.clone(),
            Err(e) => return Err(e.clone()),
        };

        match &token.token_type {
            TokenType::LeftBrace => self.parse_object(),
            TokenType::LeftBracket => self.parse_array(),
            TokenType::String(_) => {
                let token = self.advance_token()?;
                if let TokenType::String(s) = token.token_type {
                    Ok(JsonValue::String(s))
                } else {
                    unreachable!()
                }
            }
            TokenType::Number(_) => {
                let token = self.advance_token()?;
                if let TokenType::Number(n) = token.token_type {
                    Ok(JsonValue::Number(n))
                } else {
                    unreachable!()
                }
            }
            TokenType::Boolean(_) => {
                let token = self.advance_token()?;
                if let TokenType::Boolean(b) = token.token_type {
                    Ok(JsonValue::Boolean(b))
                } else {
                    unreachable!()
                }
            }
            TokenType::Null => {
                self.advance_token()?;
                Ok(JsonValue::Null)
            }
            _ => Err(ParseError::UnexpectedToken {
                expected: "JSON value".to_string(),
                found: format!("{:?}", token.token_type),
                position: token.position,
            }),
        }
    }

    fn parse_object(&mut self) -> ParseResult<JsonValue> {
        self.expect_token(TokenType::LeftBrace)?;
        let mut object = HashMap::new();

        if let Ok(token) = self.peek_token() {
            if matches!(token.token_type, TokenType::RightBrace) {
                self.advance_token()?;
                return Ok(JsonValue::Object(object));
            }
        }

        loop {
            let key_token = self.expect_token(TokenType::String(String::new()))?;
            let key = match key_token.token_type {
                TokenType::String(s) => s,
                _ => unreachable!(),
            };

            self.expect_token(TokenType::Colon)?;
            let value = self.parse_value()?;
            object.insert(key, value);

            let separator = match self.peek_token() {
                Ok(token) => token.clone(),
                Err(e) => return Err(e.clone()),
            };

            match separator.token_type {
                TokenType::RightBrace => {
                    self.advance_token()?;
                    break;
                }
                TokenType::Comma => {
                    self.advance_token()?;
                    if let Ok(next_token) = self.peek_token() {
                        if matches!(next_token.token_type, TokenType::RightBrace) {
                            return Err(ParseError::TrailingComma(next_token.position));
                        }
                    }
                }
                _ => {
                    return Err(ParseError::UnexpectedToken {
                        expected: "',' or '}'".to_string(),
                        found: format!("{:?}", separator.token_type),
                        position: separator.position,
                    });
                }
            }
        }

        Ok(JsonValue::Object(object))
    }

    fn parse_array(&mut self) -> ParseResult<JsonValue> {
        self.expect_token(TokenType::LeftBracket)?;
        let mut array = Vec::new();

        if let Ok(token) = self.peek_token() {
            if matches!(token.token_type, TokenType::RightBracket) {
                self.advance_token()?;
                return Ok(JsonValue::Array(array));
            }
        }

        loop {
            let value = self.parse_value()?;
            array.push(value);

            let separator = match self.peek_token() {
                Ok(token) => token.clone(),
                Err(e) => return Err(e.clone()),
            };

            match separator.token_type {
                TokenType::RightBracket => {
                    self.advance_token()?;
                    break;
                }
                TokenType::Comma => {
                    self.advance_token()?;
                    if let Ok(next_token) = self.peek_token() {
                        if matches!(next_token.token_type, TokenType::RightBracket) {
                            return Err(ParseError::TrailingComma(next_token.position));
                        }
                    }
                }
                _ => {
                    return Err(ParseError::UnexpectedToken {
                        expected: "',' or ']'".to_string(),
                        found: format!("{:?}", separator.token_type),
                        position: separator.position,
                    });
                }
            }
        }

        Ok(JsonValue::Array(array))
    }

    pub fn parse_single(&mut self) -> ParseResult<JsonValue> {
        let value = self.parse_value()?;
        
        let next_token = match self.peek_token() {
            Ok(token) => token.clone(),
            Err(e) => return Err(e.clone()),
        };

        if !matches!(next_token.token_type, TokenType::Eof) {
            return Err(ParseError::UnexpectedToken {
                expected: "end of input".to_string(),
                found: format!("{:?}", next_token.token_type),
                position: next_token.position,
            });
        }

        Ok(value)
    }
}

impl<R: Read> Iterator for StreamingJsonParser<R> {
    type Item = ParseResult<JsonValue>;

    fn next(&mut self) -> Option<Self::Item> {
        match self.peek_token() {
            Ok(token) if matches!(token.token_type, TokenType::Eof) => None,
            Ok(_) => Some(self.parse_value()),
            Err(e) => Some(Err(e.clone())),
        }
    }
}

pub fn parse_json_string(input: &str) -> ParseResult<JsonValue> {
    let cursor = std::io::Cursor::new(input);
    let mut parser = StreamingJsonParser::new(cursor);
    parser.parse_single()
}

pub fn parse_json_stream<R: Read>(reader: R) -> StreamingJsonParser<R> {
    StreamingJsonParser::new(reader)
}