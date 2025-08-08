#!/usr/bin/env python3
"""
Comprehensive test runner for HushMCP Email Suite
Runs all tests in the tests/ directory and provides detailed reporting.
"""

import os
import sys
import unittest
import importlib.util
import traceback
from pathlib import Path
from datetime import datetime
import subprocess

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


class TestRunner:
    def __init__(self):
        self.tests_dir = current_dir / "tests"
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def discover_test_files(self):
        """Discover all test files in the tests directory."""
        test_files = []
        for file_path in self.tests_dir.glob("test_*.py"):
            test_files.append(file_path)
        return sorted(test_files)
    
    def run_single_test_file(self, test_file):
        """Run a single test file and return results."""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_file.name}")
        print(f"{'='*60}")
        
        try:
            # Import the test module
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            if spec is None:
                raise ImportError(f"Could not load spec from {test_file}")
            
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Check if it's a unittest-based test
            if hasattr(test_module, 'unittest') or any(hasattr(test_module, attr) for attr in dir(test_module) if attr.startswith('Test')):
                return self.run_unittest_file(test_file)
            else:
                # Run as a script
                return self.run_script_test(test_file)
                
        except Exception as e:
            print(f"❌ Failed to run {test_file.name}: {e}")
            traceback.print_exc()
            return {
                'file': test_file.name,
                'status': 'failed',
                'error': str(e),
                'tests_run': 0,
                'failures': 1
            }
    
    def run_unittest_file(self, test_file):
        """Run a unittest-based test file."""
        try:
            # Create a test suite
            loader = unittest.TestLoader()
            suite = loader.discover(str(test_file.parent), pattern=test_file.name)
            
            # Run the tests
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            return {
                'file': test_file.name,
                'status': 'passed' if result.wasSuccessful() else 'failed',
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'details': result
            }
            
        except Exception as e:
            print(f"❌ Error running unittest {test_file.name}: {e}")
            return {
                'file': test_file.name,
                'status': 'failed',
                'error': str(e),
                'tests_run': 0,
                'failures': 1
            }
    
    def run_script_test(self, test_file):
        """Run a test file as a Python script."""
        try:
            print(f"Running {test_file.name} as script...")
            
            # Run the test file as a subprocess
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(current_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            status = 'passed' if result.returncode == 0 else 'failed'
            
            return {
                'file': test_file.name,
                'status': status,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'tests_run': 1
            }
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Test {test_file.name} timed out")
            return {
                'file': test_file.name,
                'status': 'timeout',
                'error': 'Test timed out after 60 seconds',
                'tests_run': 1,
                'failures': 1
            }
        except Exception as e:
            print(f"❌ Error running script {test_file.name}: {e}")
            return {
                'file': test_file.name,
                'status': 'failed',
                'error': str(e),
                'tests_run': 1,
                'failures': 1
            }
    
    def run_all_tests(self):
        """Run all discovered tests."""
        print("🚀 HushMCP Email Suite - Comprehensive Test Runner")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Tests directory: {self.tests_dir}")
        
        test_files = self.discover_test_files()
        
        if not test_files:
            print("⚠️ No test files found in tests/ directory")
            return
        
        print(f"📋 Found {len(test_files)} test files:")
        for test_file in test_files:
            print(f"   - {test_file.name}")
        
        # Run each test file
        for test_file in test_files:
            result = self.run_single_test_file(test_file)
            self.results.append(result)
            
            # Update counters
            self.total_tests += result.get('tests_run', 0)
            if result['status'] == 'passed':
                self.passed_tests += result.get('tests_run', 0)
            else:
                self.failed_tests += result.get('failures', 1)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print a comprehensive test summary."""
        print(f"\n{'='*80}")
        print("🎯 TEST SUMMARY")
        print(f"{'='*80}")
        
        print(f"📊 Overall Results:")
        print(f"   Total test files: {len(self.results)}")
        print(f"   Total tests run: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        
        success_rate = (self.passed_tests / max(self.total_tests, 1)) * 100
        print(f"   Success rate: {success_rate:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status_emoji = "✅" if result['status'] == 'passed' else "❌"
            print(f"   {status_emoji} {result['file']}: {result['status']}")
            
            if result['status'] == 'failed' and 'error' in result:
                print(f"      Error: {result['error']}")
            
            if 'tests_run' in result:
                print(f"      Tests run: {result['tests_run']}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Return overall success
        return self.failed_tests == 0


def run_environment_check():
    """Check if the environment is properly configured."""
    print("🔍 Environment Check")
    print("-" * 40)
    
    required_env_vars = [
        'SECRET_KEY',
        'VAULT_ENCRYPTION_KEY'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file configuration")
    else:
        print("✅ All required environment variables are set")
    
    # Check if key dependencies are available
    try:
        import requests
        print("✅ requests library available")
    except ImportError:
        print("❌ requests library not available - install with: pip install requests")
    
    try:
        from hushh_mcp.constants import ConsentScope
        print("✅ HushMCP framework available")
    except ImportError as e:
        print(f"❌ HushMCP framework not available: {e}")
    
    print("-" * 40)


if __name__ == "__main__":
    # Run environment check first
    run_environment_check()
    
    # Run all tests
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
