#!/usr/bin/env python3
"""
Simple Server Test - Diagnose Connection Issues
===============================================

This script helps diagnose why the server connection is failing.
"""

import subprocess
import time
import json
import sys

def check_server_process():
    """Check if server process is running."""
    print("🔍 Checking for Python server processes...")
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
        python_processes = [line for line in result.stdout.split('\n') if 'python' in line.lower()]
        
        if python_processes:
            print("✅ Found Python processes:")
            for proc in python_processes:
                print(f"   {proc.strip()}")
        else:
            print("❌ No Python processes found")
        return len(python_processes) > 0
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False

def check_port_usage():
    """Check if port 8001 is in use."""
    print("\n🔌 Checking port 8001 usage...")
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
        port_lines = [line for line in result.stdout.split('\n') if ':8001' in line]
        
        if port_lines:
            print("✅ Port 8001 activity found:")
            for line in port_lines:
                print(f"   {line.strip()}")
            return True
        else:
            print("❌ No activity on port 8001")
            return False
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def test_connection_methods():
    """Test different ways to connect to the server."""
    print("\n🌐 Testing different connection methods...")
    
    # Method 1: Using urllib (built-in)
    print("\n1️⃣ Testing with urllib...")
    try:
        import urllib.request
        response = urllib.request.urlopen("http://localhost:8001/health", timeout=5)
        data = response.read().decode()
        print(f"✅ urllib success: {data}")
    except Exception as e:
        print(f"❌ urllib failed: {e}")
    
    # Method 2: Using PowerShell
    print("\n2️⃣ Testing with PowerShell...")
    try:
        cmd = ['powershell', '-Command', 
               'Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ PowerShell success: {result.stdout}")
        else:
            print(f"❌ PowerShell failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ PowerShell test failed: {e}")
    
    # Method 3: Using requests if available
    print("\n3️⃣ Testing with requests library...")
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"✅ requests success: {response.text}")
    except ImportError:
        print("⚠️ requests library not available")
    except Exception as e:
        print(f"❌ requests failed: {e}")

def start_server_simple():
    """Start the server in a simple way."""
    print("\n🚀 Attempting to start server...")
    
    try:
        # Start server in background
        cmd = ['python', 'api.py']
        print(f"Starting: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        print(f"✅ Server started with PID: {process.pid}")
        print("⏳ Waiting 10 seconds for server to initialize...")
        
        time.sleep(10)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server process is still running")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server process exited with code: {process.returncode}")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def main():
    """Run diagnostic tests."""
    print("🔧 Server Connection Diagnostic Tool")
    print("=" * 50)
    
    # Step 1: Check current state
    has_processes = check_server_process()
    has_port = check_port_usage()
    
    # Step 2: If no server, try to start one
    if not has_processes and not has_port:
        print("\n⚠️ No server detected. Attempting to start...")
        server_process = start_server_simple()
        
        if server_process:
            # Wait and recheck
            time.sleep(5)
            check_server_process()
            check_port_usage()
    
    # Step 3: Test connections
    test_connection_methods()
    
    print("\n" + "=" * 50)
    print("🎯 Diagnostic Complete!")
    print("\n💡 Next Steps:")
    if has_processes or has_port:
        print("   ✅ Server appears to be running")
        print("   📊 Check connection test results above")
        print("   🌐 Try opening http://localhost:8001/docs in browser")
    else:
        print("   ❌ Server is not running")
        print("   🚀 Run: python api.py")
        print("   🔧 Check for dependency issues")

if __name__ == "__main__":
    main()
