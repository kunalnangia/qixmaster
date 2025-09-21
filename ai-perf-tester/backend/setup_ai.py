#!/usr/bin/env python3
"""
Setup script for AI Performance Analysis dependencies
"""
import os
import sys
import subprocess
import platform

def check_env_file():
    """Check if .env file exists and has API keys"""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    
    if not os.path.exists(env_file):
        print("\n❌ .env file not found!")
        print("Creating a template .env file...")
        
        with open(env_file, "w") as f:
            f.write("# OpenAI API Key for AI analysis features\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n\n")
            f.write("# Optional: Google Gemini API Key as an alternative\n")
            f.write("GOOGLE_API_KEY=your_google_api_key_here\n\n")
            f.write("# Optional: Model configuration\n")
            f.write("OPENAI_MODEL=gpt-4o\n")
            f.write("GOOGLE_MODEL=gemini-pro\n\n")
            f.write("# Model Priority Order (comma-separated)\n")
            f.write("AI_MODEL_PRIORITY=openai,google\n")
        
        print(f"✅ Template .env file created at: {env_file}")
        print("Please edit this file to add your API keys.\n")
        return False
    
    # Check for API keys
    with open(env_file, "r") as f:
        env_content = f.read()
    
    has_openai_key = "OPENAI_API_KEY=" in env_content and "OPENAI_API_KEY=your_openai_api_key_here" not in env_content
    has_google_key = "GOOGLE_API_KEY=" in env_content and "GOOGLE_API_KEY=your_google_api_key_here" not in env_content
    has_gemini_key = "GEMINI_API_KEY=" in env_content and "GEMINI_API_KEY=your_gemini_api_key_here" not in env_content
    
    if not (has_openai_key or has_google_key or has_gemini_key):
        print("\n⚠️ No valid API keys found in .env file!")
        print(f"Please edit {env_file} to add either an OpenAI or Google API key.\n")
        return False
    
    print("\n✅ .env file exists with API key configuration.")
    return True

def install_dependencies():
    """Install required dependencies for AI analysis"""
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_requirements.txt")
    
    if not os.path.exists(requirements_file):
        print("\n❌ ai_requirements.txt file not found!")
        return False
    
    print("\n📦 Installing AI analysis dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        return False

def main():
    """Main entry point"""
    print("=" * 60)
    print("AI Performance Analysis Setup".center(60))
    print("=" * 60)
    
    # Check environment
    print(f"\n🔍 Python version: {platform.python_version()}")
    print(f"🔍 System: {platform.system()} {platform.release()}")
    
    # Install dependencies
    deps_installed = install_dependencies()
    
    # Check .env file
    env_configured = check_env_file()
    
    # Summary
    print("\n" + "=" * 60)
    if deps_installed and env_configured:
        print("✅ Setup complete! The AI analysis system is ready to use.")
        print("\n📝 To use the AI model fallback feature:")
        print("   1. Ensure you have API keys for both OpenAI and Google")
        print("   2. Set the AI_MODEL_PRIORITY in your .env file")
        print("   3. When OpenAI quota is exceeded, the system will")
        print("      automatically fallback to Google Gemini")
    else:
        print("⚠️ Setup incomplete. Please address the issues mentioned above.")
    
    print("\nTo start the performance testing server, run:")
    print("python start.py")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()