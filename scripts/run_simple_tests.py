#!/usr/bin/env python3
"""
Simple test runner for HushMCP Email Suite
Runs basic tests without Unicode issues.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def run_simple_tests():
    """Run simple tests that don't require complex setup."""
    
    print("HushMCP Email Suite - Simple Test Runner")
    print("Started at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    tests_dir = current_dir / "tests"
    
    # List of simple test files to run
    simple_tests = [
        "test_framework_basic.py",
        "test_mailerpanda_basic.py",
        "test_mailerpanda_clean.py",
        "test_api_clean.py",
        "test_addtocalendar_basic.py"
    ]
    
    results = []
    
    for test_file in simple_tests:
        test_path = tests_dir / test_file
        
        if not test_path.exists():
            print(f"Skipping {test_file} - file not found")
            continue
        
        print(f"\nRunning: {test_file}")
        print("-" * 40)
        
        try:
            # Run the test file as a subprocess with UTF-8 encoding
            result = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=str(current_dir),
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60
            )
            
            print("Output:")
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            
            status = "PASSED" if result.returncode == 0 else "FAILED"
            print(f"Result: {status}")
            
            results.append({
                'file': test_file,
                'status': status,
                'return_code': result.returncode
            })
            
        except subprocess.TimeoutExpired:
            print(f"Test {test_file} timed out")
            results.append({
                'file': test_file,
                'status': 'TIMEOUT',
                'return_code': -1
            })
        except Exception as e:
            print(f"Error running {test_file}: {e}")
            results.append({
                'file': test_file,
                'status': 'ERROR',
                'return_code': -1
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    total = len(results)
    
    print(f"Total tests run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print("\nDetailed Results:")
    for result in results:
        status_symbol = "✓" if result['status'] == 'PASSED' else "✗"
        print(f"  {status_symbol} {result['file']}: {result['status']}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)
