#!/bin/bash

# Setup script for AI Perf Tester
echo "Setting up AI Perf Tester..."
echo

# Check if JMeter is installed
echo "Checking for JMeter installation..."
if command -v jmeter &> /dev/null
then
    echo "JMeter is already installed."
else
    echo "JMeter is not installed or not in PATH."
    echo "Please download and install JMeter from https://jmeter.apache.org/download_jmeter.cgi"
    echo "After installation, add the JMeter bin directory to your system PATH."
    echo
    read -p "Press enter to continue..."
    exit 1
fi

# Setup backend
echo "Setting up backend dependencies..."
cd ai-perf-tester/backend
pip install -r requirements.txt

# Setup frontend
echo "Setting up frontend dependencies..."
cd ../../frontend
npm install

# Install xlsx for Excel export
echo "Installing additional frontend dependencies..."
npm install xlsx

echo
echo "Setup complete!"
echo
echo "To run the application:"
echo "1. Start the backend: cd ai-perf-tester/backend && python start.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo
echo "Make sure to set your OPENAI_API_KEY environment variable for AI features."
read -p "Press enter to continue..."