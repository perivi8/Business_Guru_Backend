#!/usr/bin/env python3
"""
Test script to verify the upload-document endpoint with valid file types
"""

import requests
import os
import tempfile
from PIL import Image

def test_upload_with_valid_files():
    """Test the upload-document endpoint with valid file types"""
    
    print("🧪 Testing /api/upload-document endpoint with valid files...")
    
    # Test with PDF (create a simple text file with .pdf extension for testing)
    print("\n1. Testing with PDF file...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as pdf_file:
        pdf_file.write("%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
        pdf_file_path = pdf_file.name
    
    try:
        with open(pdf_file_path, 'rb') as test_file:
            files = {'file': ('test_document.pdf', test_file, 'application/pdf')}
            response = requests.post('http://localhost:5000/api/upload-document', files=files)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 200:
                print("   ✅ PDF upload successful!")
                file_url = response.json().get('file_url')
                print(f"   📁 File URL: {file_url}")
            else:
                print("   ❌ PDF upload failed!")
    finally:
        os.unlink(pdf_file_path)
    
    # Test with JPG (create a simple image)
    print("\n2. Testing with JPG file...")
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as jpg_file:
        jpg_file_path = jpg_file.name
    
    try:
        # Create a simple 1x1 pixel image
        img = Image.new('RGB', (1, 1), color='red')
        img.save(jpg_file_path, 'JPEG')
        
        with open(jpg_file_path, 'rb') as test_file:
            files = {'file': ('test_image.jpg', test_file, 'image/jpeg')}
            response = requests.post('http://localhost:5000/api/upload-document', files=files)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 200:
                print("   ✅ JPG upload successful!")
                file_url = response.json().get('file_url')
                print(f"   📁 File URL: {file_url}")
            else:
                print("   ❌ JPG upload failed!")
    except ImportError:
        print("   ⚠️ PIL not available, skipping image test")
    except Exception as e:
        print(f"   ❌ Image test failed: {e}")
    finally:
        if os.path.exists(jpg_file_path):
            os.unlink(jpg_file_path)

if __name__ == "__main__":
    test_upload_with_valid_files()
