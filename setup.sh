#!/bin/bash

echo "========================================"
echo "AI Lead Finder - Linux/Mac Setup Script"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ first"
    exit 1
fi

echo "[1/5] Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "Virtual environment created!"
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed!"
echo ""

# Setup .env file
echo "[5/5] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created from template"
    echo ""
    echo "========================================"
    echo "IMPORTANT: Edit .env file with your API keys!"
    echo "========================================"
    echo ""
    echo "Required API keys:"
    echo "- BRIGHT_DATA_API_KEY"
    echo "- WEB_UNLOCKER_PROXY"
    echo "- GEMINI_API_KEY"
    echo ""
else
    echo ".env file already exists"
    echo ""
fi

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: streamlit run app.py"
echo ""
echo "See QUICKSTART.md for detailed instructions"
echo ""
