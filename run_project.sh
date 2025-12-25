#!/bin/bash

# TTS Project Setup and Run Script
# This script creates a virtual environment, installs dependencies, and runs the Flask app

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting TTS Project Setup..."

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

echo "✅ Python3 is available: $(python3 --version)"

# Create virtual environment
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "✅ Virtual environment already exists and is valid"
else
    echo "🔧 Creating or recreating virtual environment..."
    python3 -m venv venv --clear  # --clear option recreates the environment
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "📦 Installing project dependencies..."
pip install -r requirements.txt

# Install additional dependencies from updated requirements.txt
echo "📦 Installing additional dependencies..."
pip install edge-tts

# Verify Flask is installed
if python -c "import flask" &> /dev/null; then
    echo "✅ Flask is installed"
else
    echo "❌ Flask installation failed"
    exit 1
fi

# Check if port 5001 is in use and kill the process if needed
echo "🔍 Checking if port 5001 is in use..."
PORT_PID=$(lsof -t -i:5001)

if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  Port 5001 is in use by process ID: $PORT_PID"
    echo "🗑️  Killing process $PORT_PID..."
    kill -9 $PORT_PID
    sleep 2  # Wait for the port to be released
    echo "✅ Process killed successfully"
else
    echo "✅ Port 5001 is free"
fi

# Run the Flask application in the background
echo "🎬 Starting Flask application on port 5001..."
python app.py &

# Get the process ID of the Flask app
FLASK_PID=$!

echo "✅ Flask application started with PID: $FLASK_PID"
echo "🌐 Application should be accessible at: http://localhost:5001"
echo "🔄 Press Ctrl+C to stop the application"

# Wait for the Flask process
wait $FLASK_PID