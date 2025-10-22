#!/usr/bin/env python3
"""
Test script to verify the upload-document endpoint is working
"""

import requests
import os
import tempfile

def test_upload_endpoint():
    """Test the upload-document endpoint"""
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("This is a test document for upload testing.")
        temp_file_path = temp_file.name
    
    try:
        print("🧪 Testing /api/upload-document endpoint...")
        
        # Test 1: POST without file (should return error)
        print("\n1. Testing POST without file...")
        response = requests.post('http://localhost:5000/api/upload-document')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test 2: POST with file (should work)
        print("\n2. Testing POST with file...")
        with open(temp_file_path, 'rb') as test_file:
            files = {'file': ('test_document.txt', test_file, 'text/plain')}
            response = requests.post('http://localhost:5000/api/upload-document', files=files)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 200:
                print("   ✅ Upload successful!")
            else:
                print("   ❌ Upload failed!")
        
        # Test 3: Test with invalid file type
        print("\n3. Testing with invalid file type...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as invalid_file:
            invalid_file.write("Invalid file type test")
            invalid_file_path = invalid_file.name
        
        try:
            with open(invalid_file_path, 'rb') as test_file:
                files = {'file': ('test_document.xyz', test_file, 'application/octet-stream')}
                response = requests.post('http://localhost:5000/api/upload-document', files=files)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
        finally:
            os.unlink(invalid_file_path)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    test_upload_endpoint()
