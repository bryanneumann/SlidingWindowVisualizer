#!/usr/bin/env python3
"""
Test runner script for the sliding window application.
Runs both Python backend tests and JavaScript frontend tests.
"""

import subprocess
import sys
import os

def run_python_tests():
    """Run Python backend tests using pytest."""
    print("🔧 Running Python Backend Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run(['pytest', 'test_app.py', '-v'], 
                               capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest first.")
        return False

def run_javascript_tests():
    """Run JavaScript frontend tests using Node.js."""
    print("\n🌐 Running JavaScript Frontend Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run(['node', 'test_frontend.js'], 
                               capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js first.")
        return False

def main():
    """Run all tests and provide summary."""
    print("🧪 Sliding Window Application Test Suite")
    print("=" * 50)
    
    python_success = run_python_tests()
    javascript_success = run_javascript_tests()
    
    print("\n📊 Test Summary")
    print("=" * 50)
    
    if python_success:
        print("✅ Python Backend Tests: PASSED")
    else:
        print("❌ Python Backend Tests: FAILED")
    
    if javascript_success:
        print("✅ JavaScript Frontend Tests: PASSED")
    else:
        print("❌ JavaScript Frontend Tests: FAILED")
    
    if python_success and javascript_success:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())