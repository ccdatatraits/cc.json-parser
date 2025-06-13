pub mod types;
pub mod lexer;
pub mod parser;

pub use types::{JsonValue, ParseError, ParseResult};
pub use parser::{StreamingJsonParser, parse_json_string, parse_json_stream};

use std::io::Read;

pub fn validate_json_string(input: &str) -> bool {
    match parse_json_string(input) {
        Ok(_) => true,
        Err(_) => false,
    }
}

pub fn stream_json_objects<R: Read>(reader: R) -> impl Iterator<Item = ParseResult<JsonValue>> {
    parse_json_stream(reader)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn test_parse_simple_string() {
        let result = parse_json_string("\"hello\"").unwrap();
        assert_eq!(result, JsonValue::String("hello".to_string()));
    }

    #[test]  
    fn test_parse_number() {
        let result = parse_json_string("42").unwrap();
        assert_eq!(result, JsonValue::Number(42.0));
    }

    #[test]
    fn test_parse_boolean() {
        let result = parse_json_string("true").unwrap();
        assert_eq!(result, JsonValue::Boolean(true));
    }

    #[test]
    fn test_parse_null() {
        let result = parse_json_string("null").unwrap();
        assert_eq!(result, JsonValue::Null);
    }

    #[test]
    fn test_parse_empty_object() {
        let result = parse_json_string("{}").unwrap();
        assert_eq!(result, JsonValue::Object(HashMap::new()));
    }

    #[test]
    fn test_parse_empty_array() {
        let result = parse_json_string("[]").unwrap();
        assert_eq!(result, JsonValue::Array(Vec::new()));
    }

    #[test]
    fn test_parse_simple_object() {
        let result = parse_json_string("{\"key\": \"value\"}").unwrap();
        let mut expected = HashMap::new();
        expected.insert("key".to_string(), JsonValue::String("value".to_string()));
        assert_eq!(result, JsonValue::Object(expected));
    }

    #[test]
    fn test_parse_simple_array() {
        let result = parse_json_string("[1, 2, 3]").unwrap();
        let expected = JsonValue::Array(vec![
            JsonValue::Number(1.0),
            JsonValue::Number(2.0),
            JsonValue::Number(3.0),
        ]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_streaming_multiple_objects() {
        let json_stream = "{\"a\": 1}\n{\"b\": 2}\n{\"c\": 3}";
        let cursor = std::io::Cursor::new(json_stream);
        let parser = parse_json_stream(cursor);
        
        let results: Vec<_> = parser.collect();
        assert_eq!(results.len(), 3);
        
        for result in results {
            assert!(result.is_ok());
        }
    }

    #[test]
    fn test_invalid_json() {
        let result = parse_json_string("{invalid}");
        assert!(result.is_err());
    }

    #[test]
    fn test_trailing_comma_error() {
        let result = parse_json_string("{\"key\": \"value\",}");
        assert!(result.is_err());
        
        if let Err(ParseError::TrailingComma(_)) = result {
            
        } else {
            panic!("Expected TrailingComma error");
        }
    }
}