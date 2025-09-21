#!/usr/bin/env python3
"""
Script to test JMeter configuration
"""
import os
import subprocess
import sys

def test_jmeter():
    """Test if JMeter is properly configured"""
    print("=" * 60)
    print("Testing JMeter Configuration")
    print("=" * 60)
    
    # Check if JMETER_HOME is set
    jmeter_home = os.environ.get('JMETER_HOME')
    if jmeter_home:
        print(f"JMETER_HOME is set to: {jmeter_home}")
        jmeter_exec = os.path.join(jmeter_home, "bin", "jmeter.bat" if os.name == 'nt' else "jmeter")
        if os.path.exists(jmeter_exec):
            print(f"Found JMeter executable at: {jmeter_exec}")
        else:
            print(f"JMeter executable not found at: {jmeter_exec}")
            jmeter_exec = None
    else:
        print("JMETER_HOME is not set")
        jmeter_exec = None
    
    # Try to run jmeter --version
    try:
        if jmeter_exec:
            result = subprocess.run([jmeter_exec, "--version"], capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(["jmeter", "--version"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("JMeter is properly configured!")
            print("Version info:")
            print(result.stdout)
            return True
        else:
            print("Failed to run JMeter:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("JMeter command timed out - possible installation issue")
    except FileNotFoundError:
        print("JMeter is not found in PATH")
        print("Please:")
        print("1. Install JMeter from https://jmeter.apache.org/download_jmeter.cgi")
        print("2. Extract it to apache-jmeter-5.6.3 directory")
        print("3. Either:")
        print("   a. Add apache-jmeter-5.6.3/bin to your system PATH")
        print("   b. Set JMETER_HOME environment variable to the JMeter installation directory")
    except Exception as e:
        print(f"Error running JMeter: {e}")
    
    return False

if __name__ == "__main__":
    success = test_jmeter()
    if success:
        print("\nJMeter is ready to use!")
    else:
        print("\nJMeter configuration needs to be fixed.")
        sys.exit(1)