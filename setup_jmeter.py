#!/usr/bin/env python3
"""
Script to help set up JMeter for the AI Perf Tester
"""
import os
import sys
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path

def check_java():
    """Check if Java is installed"""
    print("Checking for Java installation...")
    try:
        import subprocess
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("Java is already installed.")
            print("Version info:")
            # Java version info is printed to stderr
            print(result.stderr)
            return True
        else:
            print("Java is not properly configured.")
            return False
    except subprocess.TimeoutExpired:
        print("Java command timed out.")
        return False
    except FileNotFoundError:
        print("Java is not installed or not in PATH.")
        return False
    except Exception as e:
        print(f"Error checking Java: {e}")
        return False

def download_java_instructions():
    """Provide instructions for downloading Java"""
    print("\n" + "=" * 60)
    print("Java Installation Instructions")
    print("=" * 60)
    print("JMeter requires Java 8 or higher. Please install Java:")
    print("1. Go to https://adoptium.net/")
    print("2. Download OpenJDK 21 or 24 for Windows (JDK 24 recommended)")
    print("3. Run the installer and follow the installation wizard")
    print("4. After installation, set JAVA_HOME environment variable:")
    print("   - Run set_java_home.bat in this directory")
    print("   - Or manually set JAVA_HOME to your Java installation path")
    print("5. Add Java to your PATH:")
    print("   - Add %JAVA_HOME%\\bin to your system PATH")
    print("\n" + "=" * 60)

def download_jmeter():
    """Download Apache JMeter"""
    print("Downloading Apache JMeter...")
    jmeter_url = "https://dlcdn.apache.org/jmeter/binaries/apache-jmeter-5.6.3.zip"
    download_path = "apache-jmeter-5.6.3.zip"
    
    try:
        urllib.request.urlretrieve(jmeter_url, download_path)
        print(f"Downloaded JMeter to {download_path}")
        return download_path
    except Exception as e:
        print(f"Failed to download JMeter: {e}")
        print("Please download JMeter manually from https://jmeter.apache.org/download_jmeter.cgi")
        return None

def extract_jmeter(zip_path):
    """Extract JMeter archive"""
    print("Extracting JMeter...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("Extraction completed!")
        return True
    except Exception as e:
        print(f"Failed to extract JMeter: {e}")
        return False

def setup_jmeter():
    """Main setup function"""
    print("=" * 60)
    print("Setting up JMeter for AI Perf Tester")
    print("=" * 60)
    
    # Check for Java first
    if not check_java():
        download_java_instructions()
        return False
    
    # Download JMeter
    zip_path = download_jmeter()
    if not zip_path:
        return False
    
    # Extract JMeter
    if not extract_jmeter(zip_path):
        return False
    
    # Clean up zip file
    try:
        os.remove(zip_path)
        print(f"Cleaned up {zip_path}")
    except:
        pass
    
    jmeter_dir = "apache-jmeter-5.6.3"
    jmeter_bin = os.path.join(jmeter_dir, "bin")
    
    print("\n" + "=" * 60)
    print("JMeter Setup Instructions")
    print("=" * 60)
    print("JMeter has been downloaded and extracted to:")
    print(f"  {os.path.abspath(jmeter_dir)}")
    print("\nTo complete the setup, you need to add JMeter to your system PATH:")
    print("\nWindows:")
    print("  1. Open System Properties -> Advanced -> Environment Variables")
    print("  2. Under System Variables, find and select 'Path', then click 'Edit'")
    print(f"  3. Add this path: {os.path.abspath(jmeter_bin)}")
    print("  4. Click OK to save")
    print("\nAlternatively, you can set the JMETER_HOME environment variable:")
    print(f"  JMETER_HOME={os.path.abspath(jmeter_dir)}")
    print("\nAfter setting up, verify the installation by opening a new terminal and running:")
    print("  jmeter --version")
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    success = setup_jmeter()
    if success:
        print("JMeter setup completed successfully!")
        print("Please follow the instructions above to complete the configuration.")
    else:
        print("JMeter setup requires Java to be installed first.")
        print("Please install Java and run this script again.")
    
    input("Press Enter to exit...")