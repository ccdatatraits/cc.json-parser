use std::io::{Read, BufRead, BufReader};
use std::str::Chars;
use std::iter::Peekable;
use crate::types::{Token, TokenType, ParseError, ParseResult};

pub struct Lexer<R: Read> {
    reader: BufReader<R>,
    current_line: String,
    line_chars: Peekable<Chars<'static>>,
    position: usize,
    line_position: usize,
    finished: bool,
}

impl<R: Read> Lexer<R> {
    pub fn new(reader: R) -> Self {
        Self {
            reader: BufReader::new(reader),
            current_line: String::new(),
            line_chars: "".chars().peekable(),
            position: 0,
            line_position: 0,
            finished: false,
        }
    }

    fn load_next_line(&mut self) -> ParseResult<bool> {
        if self.finished {
            return Ok(false);
        }

        self.current_line.clear();
        match self.reader.read_line(&mut self.current_line) {
            Err(e) => return Err(ParseError::Io(e.to_string())),
            Ok(result) => match result {
                0 => {
                    self.finished = true;
                    Ok(false)
                }
                _ => {
                let line_ref: &'static str = unsafe {
                    std::mem::transmute(self.current_line.as_str())
                };
                    self.line_chars = line_ref.chars().peekable();
                    self.line_position = 0;
                    Ok(true)
                }
            }
        }
    }

    fn current_char(&mut self) -> ParseResult<Option<char>> {
        loop {
            if let Some(&ch) = self.line_chars.peek() {
                return Ok(Some(ch));
            }
            
            if !self.load_next_line()? {
                return Ok(None);
            }
        }
    }

    fn advance(&mut self) -> ParseResult<Option<char>> {
        if let Some(ch) = self.line_chars.next() {
            self.position += 1;
            self.line_position += 1;
            Ok(Some(ch))
        } else if self.load_next_line()? {
            self.advance()
        } else {
            Ok(None)
        }
    }

    fn skip_whitespace(&mut self) -> ParseResult<()> {
        while let Some(ch) = self.current_char()? {
            if ch.is_whitespace() {
                self.advance()?;
            } else {
                break;
            }
        }
        Ok(())
    }

    fn read_string(&mut self) -> ParseResult<String> {
        let start_pos = self.position;
        
        if self.advance()? != Some('"') {
            return Err(ParseError::InvalidCharacter {
                char: '"',
                position: start_pos,
            });
        }

        let mut result = String::new();
        let mut escaped = false;

        while let Some(ch) = self.advance()? {
            if escaped {
                match ch {
                    '"' => result.push('"'),
                    '\\' => result.push('\\'),
                    '/' => result.push('/'),
                    'b' => result.push('\u{0008}'),
                    'f' => result.push('\u{000C}'),
                    'n' => result.push('\n'),
                    'r' => result.push('\r'),
                    't' => result.push('\t'),
                    'u' => {
                        let mut hex_digits = String::new();
                        for _ in 0..4 {
                            match self.advance()? {
                                Some(hex_ch) if hex_ch.is_ascii_hexdigit() => {
                                    hex_digits.push(hex_ch);
                                }
                                _ => return Err(ParseError::InvalidEscape(self.position)),
                            }
                        }
                        let code_point = u32::from_str_radix(&hex_digits, 16)
                            .map_err(|_| ParseError::InvalidEscape(self.position))?;
                        if let Some(unicode_char) = char::from_u32(code_point) {
                            result.push(unicode_char);
                        } else {
                            return Err(ParseError::InvalidEscape(self.position));
                        }
                    }
                    _ => return Err(ParseError::InvalidEscape(self.position)),
                }
                escaped = false;
            } else if ch == '\\' {
                escaped = true;
            } else if ch == '"' {
                return Ok(result);
            } else {
                result.push(ch);
            }
        }

        Err(ParseError::UnterminatedString(start_pos))
    }

    fn read_number(&mut self) -> ParseResult<f64> {
        let start_pos = self.position;
        let mut number_str = String::new();

        if let Some('-') = self.current_char()? {
            number_str.push('-');
            self.advance()?;
        }

        if let Some(ch) = self.current_char()? {
            if ch == '0' {
                number_str.push('0');
                self.advance()?;
            } else if ch.is_ascii_digit() {
                while let Some(digit) = self.current_char()? {
                    if digit.is_ascii_digit() {
                        number_str.push(digit);
                        self.advance()?;
                    } else {
                        break;
                    }
                }
            } else {
                return Err(ParseError::InvalidNumber(start_pos));
            }
        } else {
            return Err(ParseError::InvalidNumber(start_pos));
        }

        if let Some('.') = self.current_char()? {
            number_str.push('.');
            self.advance()?;
            
            let mut has_fraction = false;
            while let Some(digit) = self.current_char()? {
                if digit.is_ascii_digit() {
                    number_str.push(digit);
                    self.advance()?;
                    has_fraction = true;
                } else {
                    break;
                }
            }
            
            if !has_fraction {
                return Err(ParseError::InvalidNumber(start_pos));
            }
        }

        if let Some(ch) = self.current_char()? {
            if ch == 'e' || ch == 'E' {
                number_str.push(ch);
                self.advance()?;
                
                if let Some(sign) = self.current_char()? {
                    if sign == '+' || sign == '-' {
                        number_str.push(sign);
                        self.advance()?;
                    }
                }
                
                let mut has_exponent = false;
                while let Some(digit) = self.current_char()? {
                    if digit.is_ascii_digit() {
                        number_str.push(digit);
                        self.advance()?;
                        has_exponent = true;
                    } else {
                        break;
                    }
                }
                
                if !has_exponent {
                    return Err(ParseError::InvalidNumber(start_pos));
                }
            }
        }

        number_str.parse::<f64>()
            .map_err(|_| ParseError::InvalidNumber(start_pos))
    }

    fn read_literal(&mut self) -> ParseResult<String> {
        let mut literal = String::new();
        
        while let Some(ch) = self.current_char()? {
            if ch.is_alphabetic() {
                literal.push(ch);
                self.advance()?;
            } else {
                break;
            }
        }
        
        Ok(literal)
    }
}

impl<R: Read> Iterator for Lexer<R> {
    type Item = ParseResult<Token>;

    fn next(&mut self) -> Option<Self::Item> {
        match self.skip_whitespace() {
            Err(e) => return Some(Err(e)),
            Ok(()) => {}
        }

        let current_pos = self.position;
        
        let ch = match self.current_char() {
            Ok(Some(ch)) => ch,
            Ok(None) => return Some(Ok(Token::new(TokenType::Eof, current_pos))),
            Err(e) => return Some(Err(e)),
        };

        let token_result = match ch {
            '{' => {
                self.advance().ok()?;
                Ok(Token::new(TokenType::LeftBrace, current_pos))
            }
            '}' => {
                self.advance().ok()?;
                Ok(Token::new(TokenType::RightBrace, current_pos))
            }
            '[' => {
                self.advance().ok()?;
                Ok(Token::new(TokenType::LeftBracket, current_pos))
            }
            ']' => {
                self.advance().ok()?;
                Ok(Token::new(TokenType::RightBracket, current_pos))
            }
            ',' => {
                self.advance().ok()?;
                Ok(Token::new(TokenType::Comma, current_pos))
            }
            ':' => {
                self.advance().ok()?;
                Ok(Token::new(TokenType::Colon, current_pos))
            }
            '"' => {
                match self.read_string() {
                    Ok(s) => Ok(Token::new(TokenType::String(s), current_pos)),
                    Err(e) => Err(e),
                }
            }
            '-' | '0'..='9' => {
                match self.read_number() {
                    Ok(n) => Ok(Token::new(TokenType::Number(n), current_pos)),
                    Err(e) => Err(e),
                }
            }
            'a'..='z' | 'A'..='Z' => {
                match self.read_literal() {
                    Ok(literal) => {
                        match literal.as_str() {
                            "true" => Ok(Token::new(TokenType::Boolean(true), current_pos)),
                            "false" => Ok(Token::new(TokenType::Boolean(false), current_pos)),
                            "null" => Ok(Token::new(TokenType::Null, current_pos)),
                            _ => Err(ParseError::InvalidCharacter {
                                char: ch,
                                position: current_pos,
                            }),
                        }
                    }
                    Err(e) => Err(e),
                }
            }
            _ => Err(ParseError::InvalidCharacter {
                char: ch,
                position: current_pos,
            }),
        };

        Some(token_result)
    }
}