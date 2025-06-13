use std::env;
use std::fs::File;
use std::io::{self, Read, BufReader};
use streaming_json_parser::{parse_json_string, parse_json_stream, JsonValue};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        eprintln!("Usage: {} <file.json> [--stream] [--validate-only] [--pretty]", args[0]);
        eprintln!("       echo '{{\"key\": \"value\"}}' | {} --stdin", args[0]);
        std::process::exit(1);
    }

    let mut stream_mode = false;
    let mut validate_only = false;
    let mut pretty_print = false;
    let mut use_stdin = false;
    let mut filename = None;

    for arg in args.iter().skip(1) {
        match arg.as_str() {
            "--stream" => stream_mode = true,
            "--validate-only" => validate_only = true,
            "--pretty" => pretty_print = true,
            "--stdin" => use_stdin = true,
            _ => {
                if filename.is_none() && !arg.starts_with("--") {
                    filename = Some(arg.clone());
                }
            }
        }
    }

    if use_stdin {
        process_stdin(stream_mode, validate_only, pretty_print)?;
    } else if let Some(file_path) = filename {
        process_file(&file_path, stream_mode, validate_only, pretty_print)?;
    } else {
        eprintln!("Error: No input file specified");
        std::process::exit(1);
    }

    Ok(())
}

fn process_stdin(stream_mode: bool, validate_only: bool, pretty_print: bool) -> Result<(), Box<dyn std::error::Error>> {
    let stdin = io::stdin();
    let reader = BufReader::new(stdin.lock());

    if stream_mode {
        process_stream(reader, validate_only, pretty_print)
    } else {
        let mut input = String::new();
        io::stdin().read_to_string(&mut input)?;
        process_single_json(&input, validate_only, pretty_print)
    }
}

fn process_file(file_path: &str, stream_mode: bool, validate_only: bool, pretty_print: bool) -> Result<(), Box<dyn std::error::Error>> {
    if stream_mode {
        let file = File::open(file_path)?;
        let reader = BufReader::new(file);
        process_stream(reader, validate_only, pretty_print)
    } else {
        let mut file = File::open(file_path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        process_single_json(&contents, validate_only, pretty_print)
    }
}

fn process_single_json(input: &str, validate_only: bool, pretty_print: bool) -> Result<(), Box<dyn std::error::Error>> {
    match parse_json_string(input) {
        Ok(json_value) => {
            if validate_only {
                println!("✓ Valid JSON");
            } else if pretty_print {
                print_json_pretty(&json_value, 0);
                println!();
            } else {
                println!("{}", json_value);
            }
            Ok(())
        }
        Err(e) => {
            eprintln!("✗ Invalid JSON: {}", e);
            std::process::exit(1);
        }
    }
}

fn process_stream<R: Read>(reader: R, validate_only: bool, pretty_print: bool) -> Result<(), Box<dyn std::error::Error>> {
    let parser = parse_json_stream(reader);
    let mut count = 0;
    let mut errors = 0;

    for result in parser {
        count += 1;
        match result {
            Ok(json_value) => {
                if validate_only {
                    if count % 1000 == 0 {
                        eprintln!("Processed {} objects...", count);
                    }
                } else if pretty_print {
                    println!("--- Object {} ---", count);
                    print_json_pretty(&json_value, 0);
                    println!();
                } else {
                    println!("{}", json_value);
                }
            }
            Err(e) => {
                errors += 1;
                eprintln!("Error in object {}: {}", count, e);
            }
        }
    }

    if validate_only {
        println!("✓ Processed {} JSON objects ({} errors)", count, errors);
    }

    if errors > 0 {
        std::process::exit(1);
    }

    Ok(())
}

fn print_json_pretty(value: &JsonValue, indent: usize) {
    let indent_str = "  ".repeat(indent);
    
    match value {
        JsonValue::String(s) => print!("\"{}\"", escape_string(s)),
        JsonValue::Number(n) => print!("{}", n),
        JsonValue::Boolean(b) => print!("{}", b),
        JsonValue::Null => print!("null"),
        JsonValue::Object(obj) => {
            println!("{{");
            let mut first = true;
            for (key, val) in obj {
                if !first {
                    println!(",");
                }
                print!("{}  \"{}\": ", indent_str, escape_string(key));
                print_json_pretty(val, indent + 1);
                first = false;
            }
            if !obj.is_empty() {
                println!();
            }
            print!("{}}}", indent_str);
        }
        JsonValue::Array(arr) => {
            println!("[");
            let mut first = true;
            for val in arr {
                if !first {
                    println!(",");
                }
                print!("{}  ", indent_str);
                print_json_pretty(val, indent + 1);
                first = false;
            }
            if !arr.is_empty() {
                println!();
            }
            print!("{}]", indent_str);
        }
    }
}

fn escape_string(s: &str) -> String {
    s.chars()
        .map(|c| match c {
            '"' => "\\\"".to_string(),
            '\\' => "\\\\".to_string(),
            '\n' => "\\n".to_string(),
            '\r' => "\\r".to_string(),
            '\t' => "\\t".to_string(),
            c if c.is_control() => format!("\\u{:04x}", c as u32),
            c => c.to_string(),
        })
        .collect()
}