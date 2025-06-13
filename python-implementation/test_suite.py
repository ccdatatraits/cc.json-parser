#!/usr/bin/env python3
import unittest
import subprocess
import sys
import json
import random
import string
import time
from pathlib import Path

class JSONParserTest(unittest.TestCase):
    """Test suite for JSON parser using unittest framework"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test files before running tests"""
        cls.config = cls._load_test_config()
        cls._create_test_files()
    
    @classmethod
    def _load_test_config(cls):
        """Load test configuration from JSON file"""
        try:
            with open('../common/test-files/test_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("test_config.json not found. Please create it first.")
    
    @classmethod 
    def _create_test_files(cls):
        """Create test files from configuration"""
        # Create files for generated tests
        for test in cls.config.get('generated_tests', []):
            with open(test['file'], 'w') as f:
                f.write(test['content'])
        
        # Create files for edge case tests  
        for test in cls.config.get('edge_case_tests', []):
            with open(test['file'], 'w') as f:
                f.write(test['content'])
    
    def run_json_parser(self, test_file):
        """Helper method to run JSON parser and return result"""
        try:
            result = subprocess.run(['python', 'json_parser.py', test_file], 
                                  capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            self.fail(f"Error running parser on {test_file}: {e}")
    
    def _run_config_tests(self, test_category, expected_exit_code=None):
        """Run tests from config for a specific category"""
        tests = self.config.get(test_category, [])
        for test in tests:
            with self.subTest(test=test['name']):
                exit_code, stdout, stderr = self.run_json_parser(test['file'])
                
                if expected_exit_code is not None:
                    self.assertEqual(exit_code, expected_exit_code, 
                                   f"{test['description']} - Expected exit code {expected_exit_code}")
                elif 'should_pass' in test:
                    expected_code = 0 if test['should_pass'] else 1
                    self.assertEqual(exit_code, expected_code, 
                                   f"{test['description']} - Expected {'valid' if test['should_pass'] else 'invalid'}")
    
    def test_valid_json_files(self):
        """Test all valid JSON files from config"""
        self._run_config_tests('valid_tests', 0)
    
    def test_invalid_json_files(self):
        """Test all invalid JSON files from config"""  
        self._run_config_tests('invalid_tests', 1)
    
    def test_generated_cases(self):
        """Test all generated test cases from config"""
        self._run_config_tests('generated_tests')
    
    def test_edge_cases(self):
        """Test all edge cases from config"""
        self._run_config_tests('edge_case_tests')
    
    def test_fuzz_random_json(self):
        """Generate and test random JSON-like strings"""
        for i in range(10):
            with self.subTest(iteration=i):
                # Generate random invalid JSON
                invalid_json = self._generate_invalid_json()
                filename = f'fuzz_invalid_{i}.json'
                
                with open(filename, 'w') as f:
                    f.write(invalid_json)
                
                exit_code, stdout, stderr = self.run_json_parser(filename)
                self.assertEqual(exit_code, 1, f"Random invalid JSON should fail: {invalid_json}")
    
    def _generate_invalid_json(self):
        """Generate random invalid JSON for fuzz testing"""
        invalid_json_patterns = [
            '{"key": }',
            '{"key" "value"}', 
            '{key: "value"}',
            '{"key": "value",}',
            '[1, 2, 3,]',
            '{"key": "unterminated',
            '{"key": 123.}',
            '{"key": .123}',
            '{123: "value"}',
            '{"": }',
            '{ "key" : }',
            '[,1,2,3]',
            '{"a":{"b":}}'
        ]
        
        chosen_pattern = random.choice(invalid_json_patterns)
        # Add some random noise
        if random.random() < 0.3:
            chosen_pattern += random.choice(['{', '}', '[', ']', ',', '"'])
        
        return chosen_pattern
    
    def test_performance_large_object(self):
        """Test performance with large JSON object"""
        # Generate large JSON object
        large_obj = {}
        for i in range(1000):
            large_obj[f'key_{i}'] = f'value_{i}' * 10
        
        large_json = json.dumps(large_obj)
        filename = 'performance_large.json'
        
        with open(filename, 'w') as f:
            f.write(large_json)
        
        # Measure parsing time
        start_time = time.time()
        exit_code, stdout, stderr = self.run_json_parser(filename)
        end_time = time.time()
        
        parse_time = end_time - start_time
        self.assertEqual(exit_code, 0, "Large JSON should parse successfully")
        self.assertLess(parse_time, 5.0, f"Large JSON took too long to parse: {parse_time:.2f}s")
    
    def test_performance_deeply_nested(self):
        """Test performance with deeply nested JSON"""
        # Create deeply nested structure
        nested = "null"
        for i in range(100):
            nested = f'{{"level_{i}":{nested}}}'
        
        filename = 'performance_nested.json'
        with open(filename, 'w') as f:
            f.write(nested)
        
        # Measure parsing time
        start_time = time.time()
        exit_code, stdout, stderr = self.run_json_parser(filename)
        end_time = time.time()
        
        parse_time = end_time - start_time
        self.assertEqual(exit_code, 0, "Deeply nested JSON should parse successfully")
        self.assertLess(parse_time, 2.0, f"Deeply nested JSON took too long: {parse_time:.2f}s")
    
    def test_performance_large_array(self):
        """Test performance with large JSON array"""
        # Generate large array
        large_array = []
        for i in range(10000):
            large_array.append({
                'id': i,
                'name': f'item_{i}',
                'active': i % 2 == 0,
                'score': i * 0.1
            })
        
        large_json = json.dumps(large_array)
        filename = 'performance_array.json'
        
        with open(filename, 'w') as f:
            f.write(large_json)
        
        # Measure parsing time
        start_time = time.time()
        exit_code, stdout, stderr = self.run_json_parser(filename)
        end_time = time.time()
        
        parse_time = end_time - start_time
        self.assertEqual(exit_code, 0, "Large array should parse successfully")
        self.assertLess(parse_time, 10.0, f"Large array took too long: {parse_time:.2f}s")

class JSONParserBenchmark:
    """Benchmark suite for JSON parser performance"""
    
    def __init__(self):
        self.results = {}
    
    def run_benchmark(self, benchmark_name, json_content, iteration_count=5):
        """Run benchmark for given JSON content"""
        benchmark_filename = f'benchmark_{benchmark_name}.json'
        with open(benchmark_filename, 'w') as benchmark_file:
            benchmark_file.write(json_content)
        
        execution_times = []
        for _ in range(iteration_count):
            start_time = time.time()
            parsing_result = subprocess.run(['python', 'json_parser.py', benchmark_filename], 
                                  capture_output=True, text=True)
            end_time = time.time()
            
            if parsing_result.returncode == 0:
                execution_times.append(end_time - start_time)
        
        if execution_times:
            average_execution_time = sum(execution_times) / len(execution_times)
            fastest_execution_time = min(execution_times)
            slowest_execution_time = max(execution_times)
            
            self.results[benchmark_name] = {
                'avg': average_execution_time,
                'min': fastest_execution_time, 
                'max': slowest_execution_time,
                'iterations': len(execution_times)
            }
    
    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*50)
        print("JSON Parser Performance Benchmark")
        print("="*50)
        
        for benchmark_name, benchmark_result in self.results.items():
            print(f"{benchmark_name:<20} | Avg: {benchmark_result['avg']:.4f}s | "
                  f"Min: {benchmark_result['min']:.4f}s | Max: {benchmark_result['max']:.4f}s")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--benchmark':
        # Run benchmarks
        performance_benchmark = JSONParserBenchmark()
        
        # Simple benchmarks
        performance_benchmark.run_benchmark('empty_object', '{}')
        performance_benchmark.run_benchmark('simple_string', '"hello world"')
        performance_benchmark.run_benchmark('number', '12345')
        
        # More complex benchmarks
        medium_sized_object = {f'key_{i}': f'value_{i}' for i in range(100)}
        performance_benchmark.run_benchmark('medium_object', json.dumps(medium_sized_object))
        
        medium_sized_array = list(range(1000))
        performance_benchmark.run_benchmark('medium_array', json.dumps(medium_sized_array))
        
        performance_benchmark.print_results()
    else:
        # Run normal tests
        unittest.main(verbosity=2)