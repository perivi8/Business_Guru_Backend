#!/usr/bin/env bash
# exit on error
set -o errexit

# Clean Python cache files that might cause build issues
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Install system dependencies
apt-get update
apt-get install -y libmagic1 tesseract-ocr

# Install Python dependencies
python3.11 -m pip install --upgrade pip
python3.11 -m pip install --no-cache-dir -r requirements.txt