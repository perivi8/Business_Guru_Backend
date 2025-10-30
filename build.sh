#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y libmagic1 tesseract-ocr

# Install Python dependencies
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt
