#!/usr/bin/env python3
"""
Script to troubleshoot JMeter and Java configuration
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_java():
    """Check Java installation and configuration"""
    print("\n=== Checking Java Installation ===")
    
    # Check JAVA_HOME
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        print(f"JAVA_HOME is set to: {java_home}")
        if os.path.exists(java_home):
            print(f"✅ JAVA_HOME directory exists")
            
            # Check java executable in JAVA_HOME
            java_exec = os.path.join(java_home, "bin", "java.exe" if os.name == 'nt' else "java")
            if os.path.exists(java_exec):
                print(f"✅ Java executable found at: {java_exec}")
            else:
                print(f"❌ Java executable not found at: {java_exec}")
        else:
            print(f"❌ JAVA_HOME directory does not exist")
    else:
        print("❌ JAVA_HOME environment variable is not set")
    
    # Check java in PATH
    java_in_path = shutil.which("java")
    if java_in_path:
        print(f"✅ Java found in PATH: {java_in_path}")
        
        # Try to get java version
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, text=True)
            print(f"Java version info (stderr):")
            print(result.stderr.strip())
        except Exception as e:
            print(f"❌ Error running java -version: {e}")
    else:
        print("❌ Java not found in PATH")

def check_jmeter():
    """Check JMeter installation and configuration"""
    print("\n=== Checking JMeter Installation ===")
    
    # Check JMETER_HOME
    jmeter_home = os.environ.get('JMETER_HOME')
    if jmeter_home:
        print(f"JMETER_HOME is set to: {jmeter_home}")
        if os.path.exists(jmeter_home):
            print(f"✅ JMETER_HOME directory exists")
            
            # Check jmeter executable in JMETER_HOME
            jmeter_exec = os.path.join(jmeter_home, "bin", "jmeter.bat" if os.name == 'nt' else "jmeter")
            if os.path.exists(jmeter_exec):
                print(f"✅ JMeter executable found at: {jmeter_exec}")
                
                # Try to run jmeter
                try:
                    result = subprocess.run([jmeter_exec, "--version"], capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ JMeter version: {result.stdout.strip()}")
                    else:
                        print(f"❌ Error running JMeter: {result.stderr.strip()}")
                except Exception as e:
                    print(f"❌ Error running JMeter: {e}")
            else:
                print(f"❌ JMeter executable not found at: {jmeter_exec}")
        else:
            print(f"❌ JMETER_HOME directory does not exist")
    else:
        print("❌ JMETER_HOME environment variable is not set")
    
    # Check jmeter in PATH
    jmeter_in_path = shutil.which("jmeter")
    if jmeter_in_path:
        print(f"✅ JMeter found in PATH: {jmeter_in_path}")
    else:
        print("❌ JMeter not found in PATH")
    
    # Look for JMeter in common locations
    print("\nLooking for JMeter in common locations...")
    possible_locations = [
        # Current directory
        os.path.join(os.getcwd(), "apache-jmeter-5.6.3", "bin", "jmeter.bat"),
        # Parent directory 
        os.path.join(os.path.dirname(os.getcwd()), "apache-jmeter-5.6.3", "bin", "jmeter.bat"),
        # Root of project
        os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "apache-jmeter-5.6.3", "bin", "jmeter.bat"),
    ]
    
    found = False
    for location in possible_locations:
        if os.path.exists(location):
            print(f"✅ JMeter executable found at: {location}")
            found = True
    
    if not found:
        print("❌ JMeter not found in any common locations")

def main():
    """Main function"""
    print("=" * 60)
    print("Java and JMeter Configuration Troubleshooter")
    print("=" * 60)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Parent directory: {os.path.dirname(os.getcwd())}")
    
    # Print environment variables
    print("\n=== Environment Variables ===")
    for var in ['JAVA_HOME', 'JMETER_HOME', 'PATH']:
        print(f"{var}: {os.environ.get(var, 'Not set')}")
    
    # Check Java
    check_java()
    
    # Check JMeter
    check_jmeter()
    
    # Provide recommendations
    print("\n=== Recommendations ===")
    if not os.environ.get('JAVA_HOME'):
        print("1. Set JAVA_HOME environment variable to your Java installation directory")
        print("   Example: JAVA_HOME=C:\\Program Files\\Java\\jdk-24")
    
    if not os.environ.get('JMETER_HOME'):
        print("2. Set JMETER_HOME environment variable to your JMeter installation directory")
        print("   Example: JMETER_HOME=C:\\Users\\kunal\\Downloads\\qix-master\\qix-master\\apache-jmeter-5.6.3")
    
    print("3. Make sure JMeter's bin directory is in your PATH")
    print("4. Make sure Java's bin directory is in your PATH")
    print("5. Restart your terminal after making these changes")
    print("6. Run 'java -version' and 'jmeter --version' to verify")

if __name__ == "__main__":
    main()