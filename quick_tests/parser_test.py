#!/usr/bin/env python3
import sys
import os
from typing import List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import the parser function
from utils.parsers import parse_openssh_log_line
from utils.parsers import parse_hdfs_log_line

def test_openssh_parser(log_file_path: str) -> None:
    """
    Test the OpenSSH log parser on all lines in a log file.
    
    Args:
        log_file_path: Path to the OpenSSH log file
    """
    if not os.path.exists(log_file_path):
        print(f"Error: File not found: {log_file_path}")
        sys.exit(1)
    
    successful_parses = 0
    failed_parses = 0
    failed_lines: List[Tuple[int, str, Exception]] = []
    
    print(f"Testing OpenSSH parser on: {log_file_path}")
    print("-" * 80)
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        total_lines = 0
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            total_lines += 1
            try:
                parsed_data, formatted_string = parse_openssh_log_line(line)
                successful_parses += 1
                
                # Optional: Print occasional successful parse for verification
                # if successful_parses % 1000 == 0:
                #     print(f"Sample successful parse (line {line_num}):")
                #     print(f"  Original: {line}")
                #     print(f"  Parsed timestamp: {parsed_data['timestamp']}")
                #     print(f"  Log level: {parsed_data['labels']['log_level']}")
                #     print("-" * 40)
                    
            except Exception as e:
                failed_parses += 1
                if len(failed_lines) < 10:  # Keep track of first 10 failures
                    failed_lines.append((line_num, line, e))
    
    # Print statistics
    success_percentage = (successful_parses / total_lines) * 100 if total_lines > 0 else 0
    print(f"\nParser Test Results:")
    print(f"Total lines processed: {total_lines}")
    print(f"Successful parses: {successful_parses} ({success_percentage:.2f}%)")
    print(f"Failed parses: {failed_parses} ({100 - success_percentage:.2f}%)")
    
    # Print examples of failed parses if any
    if failed_lines:
        print("\nExamples of failed parses:")
        for i, (line_num, line, error) in enumerate(failed_lines, 1):
            print(f"\n{i}. Line {line_num}: {line}")
            print(f"   Error: {type(error).__name__}: {str(error)}")
    else:
        print("\nNo parsing failures detected! ✓")
    
    print("\nTest completed.")

def test_hdfs_parser(log_file_path: str) -> None:
    """
    Test the HDFS log parser on all lines in a log file.
    
    Args:
        log_file_path: Path to the HDFS log file
    """
    if not os.path.exists(log_file_path):
        print(f"Error: File not found: {log_file_path}")
        sys.exit(1)
    
    successful_parses = 0
    failed_parses = 0
    failed_lines: List[Tuple[int, str, Exception]] = []
    
    print(f"Testing HDFS parser on: {log_file_path}")
    print("-" * 80)
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        total_lines = 0
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            total_lines += 1
            try:
                parsed_data, formatted_string = parse_hdfs_log_line(line)
                successful_parses += 1
                
                # Optional: Print occasional successful parse for verification
                # if successful_parses % 1000 == 0:
                #     print(f"Sample successful parse (line {line_num}):")
                #     print(f"  Original: {line}")
                #     print(f"  Parsed timestamp: {parsed_data['timestamp']}")
                #     print(f"  Log level: {parsed_data['labels']['log_level']}")
                #     print("-" * 40)
                    
            except Exception as e:
                failed_parses += 1
                if len(failed_lines) < 10:  # Keep track of first 10 failures
                    failed_lines.append((line_num, line, e))
    
    # Print statistics
    success_percentage = (successful_parses / total_lines) * 100 if total_lines > 0 else 0
    print(f"\nParser Test Results:")
    print(f"Total lines processed: {total_lines}")
    print(f"Successful parses: {successful_parses} ({success_percentage:.2f}%)")
    print(f"Failed parses: {failed_parses} ({100 - success_percentage:.2f}%)")
    
    # Print examples of failed parses if any
    if failed_lines:
        print("\nExamples of failed parses:")
        for i, (line_num, line, error) in enumerate(failed_lines, 1):
            print(f"\n{i}. Line {line_num}: {line}")
            print(f"   Error: {type(error).__name__}: {str(error)}")
    else:
        print("\nNo parsing failures detected! ✓")
    
    print("\nTest completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser_test.py <parser_type> <path_to_log_file>")
        print("  parser_type: 'openssh' or 'hdfs'")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Backward compatibility: Assume OpenSSH parser
        log_file_path = sys.argv[1]
        test_openssh_parser(log_file_path)
    else:
        parser_type = sys.argv[1].lower()
        log_file_path = sys.argv[2]
        
        if parser_type == "openssh":
            test_openssh_parser(log_file_path)
        elif parser_type == "hdfs":
            test_hdfs_parser(log_file_path)
        else:
            print(f"Unknown parser type: {parser_type}")
            print("Supported types: 'openssh', 'hdfs'")
            sys.exit(1)