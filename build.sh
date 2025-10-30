#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Build started ==="
echo "Current directory: $(pwd)"

# Explicitly use Python 3.11
PYTHON_CMD=python3.11
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Python 3.11 not found, trying python3"
    PYTHON_CMD=python3
fi

echo "Using Python command: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"

# Clean Python cache files that might cause build issues
echo "Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y libmagic1 tesseract-ocr

# Create virtual environment to isolate dependencies
echo "Creating virtual environment..."
$PYTHON_CMD -m venv .venv
source .venv/bin/activate

echo "Upgrading pip in virtual environment..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --no-cache-dir -r requirements.txt

echo "=== Build completed successfully ==="