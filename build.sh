#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y libmagic1 tesseract-ocr

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
