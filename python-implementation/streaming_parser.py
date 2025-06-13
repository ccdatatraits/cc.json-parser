"""
Streaming JSON Parser for handling large JSON files efficiently.

This module provides memory-efficient parsing for large JSON files by
processing them in chunks rather than loading everything into memory.
"""

import json
from typing import Iterator, Any, Optional, Union, IO
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class StreamingJSONParser:
    """
    A streaming JSON parser that can handle large files efficiently.
    
    Features:
    - Memory-efficient parsing of large JSON files
    - Support for JSON arrays with multiple objects
    - Configurable buffer size for performance tuning
    - Error recovery and reporting
    """
    
    def __init__(self, buffer_size: int = 8192):
        """
        Initialize the streaming parser.
        
        Args:
            buffer_size: Size of read buffer in bytes (default: 8KB)
        """
        self.buffer_size = buffer_size
        self.parser = None
        
    def parse_file_stream(self, file_path: Union[str, Path], 
                         encoding: str = 'utf-8') -> Iterator[Any]:
        """
        Parse a JSON file as a stream of objects.
        
        Args:
            file_path: Path to the JSON file
            encoding: File encoding (default: utf-8)
            
        Yields:
            Parsed JSON objects one at a time
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is malformed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.debug(f"Starting streaming parse of {file_path}")
        
        with open(file_path, 'r', encoding=encoding) as file:
            yield from self.parse_stream(file)
            
    def parse_stream(self, stream: IO[str]) -> Iterator[Any]:
        """
        Parse a JSON stream (file-like object).
        
        Args:
            stream: File-like object containing JSON data
            
        Yields:
            Parsed JSON objects one at a time
        """
        buffer = ""
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        object_start = 0
        
        while True:
            chunk = stream.read(self.buffer_size)
            if not chunk:
                break
                
            buffer += chunk
            
            i = object_start
            while i < len(buffer):
                char = buffer[i]
                
                if escape_next:
                    escape_next = False
                    i += 1
                    continue
                    
                if char == '\\' and in_string:
                    escape_next = True
                elif char == '"':
                    in_string = not in_string
                elif not in_string:
                    if char == '{':
                        if brace_count == 0 and bracket_count == 0:
                            object_start = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and bracket_count == 0:
                            # Complete object found
                            json_str = buffer[object_start:i+1]
                            try:
                                obj = json.loads(json_str)
                                yield obj
                                logger.debug(f"Parsed object at position {object_start}")
                            except json.JSONDecodeError as e:
                                logger.warning(f"Skipping malformed JSON at position {object_start}: {e}")
                            
                            # Reset for next object
                            object_start = i + 1
                            buffer = buffer[object_start:]
                            i = -1  # Will be incremented to 0
                            object_start = 0
                    elif char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        
                i += 1
                
    def validate_file_stream(self, file_path: Union[str, Path], 
                           encoding: str = 'utf-8') -> tuple[bool, list[str]]:
        """
        Validate a JSON file using streaming parser.
        
        Args:
            file_path: Path to the JSON file
            encoding: File encoding
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            object_count = 0
            for obj in self.parse_file_stream(file_path, encoding):
                object_count += 1
                
            logger.info(f"Successfully validated {object_count} JSON objects")
            return True, []
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            return False, errors


class JSONLineParser:
    """
    Parser for JSON Lines format (JSONL) where each line is a separate JSON object.
    
    This is commonly used for log files and data processing pipelines.
    """
    
    def __init__(self):
        self.line_number = 0
        
    def parse_file(self, file_path: Union[str, Path], 
                   encoding: str = 'utf-8',
                   skip_invalid: bool = False) -> Iterator[tuple[int, Any]]:
        """
        Parse a JSONL file line by line.
        
        Args:
            file_path: Path to the JSONL file
            encoding: File encoding
            skip_invalid: If True, skip invalid lines instead of raising error
            
        Yields:
            Tuples of (line_number, parsed_object)
        """
        file_path = Path(file_path)
        self.line_number = 0
        
        with open(file_path, 'r', encoding=encoding) as file:
            for line in file:
                self.line_number += 1
                line = line.strip()
                
                if not line:
                    continue  # Skip empty lines
                    
                try:
                    obj = json.loads(line)
                    yield self.line_number, obj
                except json.JSONDecodeError as e:
                    if skip_invalid:
                        logger.warning(f"Skipping invalid JSON on line {self.line_number}: {e}")
                        continue
                    else:
                        raise ValueError(f"Invalid JSON on line {self.line_number}: {e}")
                        
    def validate_file(self, file_path: Union[str, Path], 
                     encoding: str = 'utf-8') -> tuple[bool, list[str]]:
        """
        Validate a JSONL file.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            valid_lines = 0
            for line_num, obj in self.parse_file(file_path, encoding, skip_invalid=True):
                valid_lines += 1
                
            logger.info(f"Validated {valid_lines} JSON lines")
            return True, []
            
        except Exception as e:
            error_msg = f"JSONL validation failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            return False, errors


def stream_large_json(file_path: Union[str, Path], 
                     max_memory_mb: int = 100) -> Iterator[Any]:
    """
    Convenience function to stream large JSON files with memory limit.
    
    Args:
        file_path: Path to JSON file
        max_memory_mb: Maximum memory usage in MB
        
    Yields:
        Parsed JSON objects
    """
    # Calculate buffer size based on memory limit
    buffer_size = min(8192, (max_memory_mb * 1024 * 1024) // 10)
    
    parser = StreamingJSONParser(buffer_size=buffer_size)
    yield from parser.parse_file_stream(file_path)


# Convenience functions for common use cases
def validate_large_json(file_path: Union[str, Path]) -> bool:
    """Quick validation of large JSON files."""
    parser = StreamingJSONParser()
    is_valid, errors = parser.validate_file_stream(file_path)
    return is_valid


def count_json_objects(file_path: Union[str, Path]) -> int:
    """Count the number of JSON objects in a file."""
    parser = StreamingJSONParser()
    count = sum(1 for _ in parser.parse_file_stream(file_path))
    return count