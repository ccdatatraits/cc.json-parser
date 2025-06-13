#!/usr/bin/env python3
import sys
import argparse
import json
import logging
from pathlib import Path
from parser import parse_json, is_valid_json

def main():
    parser = argparse.ArgumentParser(
        description='JSON Parser - validates and processes JSON input',
        epilog='Examples:\n'
               '  %(prog)s file.json                    # Validate file\n'
               '  echo \'{"key": "value"}\' | %(prog)s   # Validate from stdin\n'
               '  %(prog)s --pretty file.json           # Pretty print JSON\n'
               '  %(prog)s --validate-only file.json    # Just validate, no output',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('file', nargs='?', help='JSON file to parse (if not provided, reads from stdin)')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty print the JSON output')
    parser.add_argument('--validate-only', '-v', action='store_true', help='Only validate, do not output parsed JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress error messages')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--encoding', default='utf-8', help='Input file encoding (default: utf-8)')
    parser.add_argument('--version', action='version', version='JSON Parser 1.0.0')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    try:
        # Read input
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                if not args.quiet:
                    print(f"Error: File '{args.file}' not found", file=sys.stderr)
                sys.exit(1)
            
            logger.debug(f"Reading file: {file_path}")
            try:
                with open(file_path, 'r', encoding=args.encoding) as f:
                    json_text = f.read()
            except UnicodeDecodeError as e:
                if not args.quiet:
                    print(f"Error: Cannot decode file with {args.encoding} encoding: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            logger.debug("Reading from stdin")
            json_text = sys.stdin.read()
        
        if not json_text.strip():
            if not args.quiet:
                print("Error: Empty input", file=sys.stderr)
            sys.exit(1)
        
        logger.debug(f"Input length: {len(json_text)} characters")
        
        # Parse and validate
        try:
            parsed_data = parse_json(json_text)
            logger.debug("JSON validation successful")
            
            if not args.validate_only:
                # Format output
                if args.pretty:
                    output = json.dumps(parsed_data, indent=2, ensure_ascii=False)
                else:
                    output = json.dumps(parsed_data, separators=(',', ':'), ensure_ascii=False)
                
                # Write output
                if args.output:
                    output_path = Path(args.output)
                    logger.debug(f"Writing to file: {output_path}")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(output)
                        f.write('\n')
                else:
                    print(output)
            
            sys.exit(0)  # Valid JSON
            
        except ValueError as e:
            logger.debug(f"JSON validation failed: {e}")
            if not args.quiet:
                print(f"Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        if not args.quiet:
            print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.debug(f"Unexpected error: {e}", exc_info=True)
        if not args.quiet:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()