#!/bin/bash
# Setup script for OpenAI Responses Starter App
# This script installs Python dependencies and Playwright browsers

set -e  # Exit on error

echo "🚀 Setting up OpenAI Responses Starter App..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check if virtual environment exists
if [ -d ".venv" ] && [ -f ".venv/bin/python" ]; then
    echo "📦 Virtual environment detected (.venv)"
    PYTHON_CMD=".venv/bin/python"
    PIP_CMD=".venv/bin/pip"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

echo "📦 Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

echo ""
echo "🌐 Installing Playwright browsers..."
$PYTHON_CMD -m playwright install chromium

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the app, run:"
echo "  python start.py"
echo ""
echo "Or start manually:"
echo "  Backend:  cd backend && uvicorn main:app --reload --port 8000"
echo "  Frontend: cd frontend && streamlit run app.py --server.port 8501"

