#!/bin/bash

# Script to run the trading bot web interface locally

echo "🚀 Starting 9:15 Trading Bot Web Interface..."
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Set environment variables for development
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key-change-in-production

echo ""
echo "✅ Setup complete!"
echo "================================================"
echo "🌐 Starting web server..."
echo ""
echo "📱 Access the dashboard at:"
echo "   http://localhost:5000"
echo ""
echo "🔐 Demo Login Credentials:"
echo "   Username: demo"
echo "   Password: demo123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"
echo ""

# Run the Flask application
python app.py