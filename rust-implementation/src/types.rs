use std::collections::HashMap;
use std::fmt;
use thiserror::Error;

#[derive(Debug, Clone, PartialEq)]
pub enum TokenType {
    LeftBrace,
    RightBrace,
    LeftBracket,
    RightBracket,
    Comma,
    Colon,
    String(String),
    Number(f64),
    Boolean(bool),
    Null,
    Eof,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Token {
    pub token_type: TokenType,
    pub position: usize,
}

impl Token {
    pub fn new(token_type: TokenType, position: usize) -> Self {
        Self {
            token_type,
            position,
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum JsonValue {
    String(String),
    Number(f64),
    Boolean(bool),
    Null,
    Object(HashMap<String, JsonValue>),
    Array(Vec<JsonValue>),
}

impl fmt::Display for JsonValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            JsonValue::String(s) => write!(f, "\"{}\"", s),
            JsonValue::Number(n) => write!(f, "{}", n),
            JsonValue::Boolean(b) => write!(f, "{}", b),
            JsonValue::Null => write!(f, "null"),
            JsonValue::Object(obj) => {
                write!(f, "{{")?;
                let mut first = true;
                for (key, value) in obj {
                    if !first {
                        write!(f, ",")?;
                    }
                    write!(f, "\"{}\":{}", key, value)?;
                    first = false;
                }
                write!(f, "}}")
            }
            JsonValue::Array(arr) => {
                write!(f, "[")?;
                let mut first = true;
                for value in arr {
                    if !first {
                        write!(f, ",")?;
                    }
                    write!(f, "{}", value)?;
                    first = false;
                }
                write!(f, "]")
            }
        }
    }
}

#[derive(Error, Debug, Clone)]
pub enum ParseError {
    #[error("Unexpected end of input at position {0}")]
    UnexpectedEof(usize),
    
    #[error("Invalid character '{char}' at position {position}")]
    InvalidCharacter { char: char, position: usize },
    
    #[error("Invalid number format at position {0}")]
    InvalidNumber(usize),
    
    #[error("Unterminated string at position {0}")]
    UnterminatedString(usize),
    
    #[error("Invalid escape sequence at position {0}")]
    InvalidEscape(usize),
    
    #[error("Expected {expected}, found {found} at position {position}")]
    UnexpectedToken {
        expected: String,
        found: String,
        position: usize,
    },
    
    #[error("Trailing comma not allowed at position {0}")]
    TrailingComma(usize),
    
    #[error("Invalid JSON structure at position {0}")]
    InvalidStructure(usize),
    
    #[error("IO error: {0}")]
    Io(String),
}

pub type ParseResult<T> = Result<T, ParseError>;