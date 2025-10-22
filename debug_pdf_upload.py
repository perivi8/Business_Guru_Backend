#!/usr/bin/env python3
"""
Debug script to test PDF upload to Cloudinary
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Cloudinary import and configuration
print("🔍 Testing Cloudinary configuration...")
print("=" * 50)

try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    print("✅ Cloudinary library imported successfully")
except ImportError as e:
    print(f"❌ Cloudinary import failed: {e}")
    sys.exit(1)

# Check environment variables
CLOUDINARY_ENABLED = os.getenv('CLOUDINARY_ENABLED', 'false').lower() == 'true'
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

print(f"CLOUDINARY_ENABLED: {CLOUDINARY_ENABLED}")
print(f"CLOUDINARY_CLOUD_NAME: {CLOUDINARY_CLOUD_NAME}")
print(f"CLOUDINARY_API_KEY: {'Set' if CLOUDINARY_API_KEY else 'Not set'}")
print(f"CLOUDINARY_API_SECRET: {'Set' if CLOUDINARY_API_SECRET else 'Not set'}")

if not all([CLOUDINARY_ENABLED, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    print("❌ Cloudinary configuration incomplete!")
    print("Please check your environment variables.")
    sys.exit(1)

# Initialize Cloudinary
try:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )
    print(f"✅ Cloudinary initialized successfully with cloud: {CLOUDINARY_CLOUD_NAME}")
except Exception as e:
    print(f"❌ Failed to initialize Cloudinary: {str(e)}")
    sys.exit(1)

print("\n🧪 Testing PDF upload scenarios...")
print("=" * 50)

def create_test_pdf():
    """Create a simple test PDF file"""
    pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        f.write(pdf_content)
        return f.name

def test_pdf_upload_scenarios():
    """Test different PDF upload scenarios"""
    
    # Create test PDF
    pdf_file_path = create_test_pdf()
    
    try:
        print(f"📄 Created test PDF: {pdf_file_path}")
        
        # Test 1: Upload with resource_type="raw" (current implementation)
        print("\n1️⃣ Testing with resource_type='raw' (current implementation)")
        try:
            with open(pdf_file_path, 'rb') as f:
                result = cloudinary.uploader.upload(
                    f,
                    folder="tmis-business-guru/test",
                    public_id="test_pdf_raw",
                    resource_type="raw",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=True
                )
            print(f"✅ SUCCESS with resource_type='raw'")
            print(f"   Public ID: {result['public_id']}")
            print(f"   URL: {result['secure_url']}")
            print(f"   Format: {result['format']}")
            print(f"   Bytes: {result['bytes']}")
            
            # Clean up
            cloudinary.uploader.destroy(result['public_id'], resource_type="raw")
            
        except Exception as e:
            print(f"❌ FAILED with resource_type='raw': {str(e)}")
        
        # Test 2: Upload with resource_type="auto"
        print("\n2️⃣ Testing with resource_type='auto'")
        try:
            with open(pdf_file_path, 'rb') as f:
                result = cloudinary.uploader.upload(
                    f,
                    folder="tmis-business-guru/test",
                    public_id="test_pdf_auto",
                    resource_type="auto",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=True
                )
            print(f"✅ SUCCESS with resource_type='auto'")
            print(f"   Public ID: {result['public_id']}")
            print(f"   URL: {result['secure_url']}")
            print(f"   Format: {result['format']}")
            print(f"   Bytes: {result['bytes']}")
            
            # Clean up
            cloudinary.uploader.destroy(result['public_id'], resource_type="auto")
            
        except Exception as e:
            print(f"❌ FAILED with resource_type='auto': {str(e)}")
        
        # Test 3: Upload with resource_type="image" (should fail for PDF)
        print("\n3️⃣ Testing with resource_type='image' (should fail)")
        try:
            with open(pdf_file_path, 'rb') as f:
                result = cloudinary.uploader.upload(
                    f,
                    folder="tmis-business-guru/test",
                    public_id="test_pdf_image",
                    resource_type="image",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=True
                )
            print(f"⚠️ UNEXPECTED SUCCESS with resource_type='image'")
            print(f"   Public ID: {result['public_id']}")
            print(f"   URL: {result['secure_url']}")
            
            # Clean up
            cloudinary.uploader.destroy(result['public_id'], resource_type="image")
            
        except Exception as e:
            print(f"✅ EXPECTED FAILURE with resource_type='image': {str(e)}")
        
        # Test 4: Upload without specifying resource_type (default)
        print("\n4️⃣ Testing without resource_type (default)")
        try:
            with open(pdf_file_path, 'rb') as f:
                result = cloudinary.uploader.upload(
                    f,
                    folder="tmis-business-guru/test",
                    public_id="test_pdf_default",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=True
                )
            print(f"✅ SUCCESS with default resource_type")
            print(f"   Public ID: {result['public_id']}")
            print(f"   URL: {result['secure_url']}")
            print(f"   Format: {result['format']}")
            print(f"   Bytes: {result['bytes']}")
            
            # Clean up
            cloudinary.uploader.destroy(result['public_id'])
            
        except Exception as e:
            print(f"❌ FAILED with default resource_type: {str(e)}")
            
    finally:
        # Clean up test file
        if os.path.exists(pdf_file_path):
            os.unlink(pdf_file_path)
            print(f"\n🧹 Cleaned up test file: {pdf_file_path}")

def test_file_extension_detection():
    """Test the file extension detection logic"""
    print("\n🔍 Testing file extension detection logic...")
    print("=" * 50)
    
    test_cases = [
        "document.pdf",
        "Document.PDF", 
        "file.with.dots.pdf",
        "no_extension",
        "image.jpg",
        "archive.zip",
        "text.txt"
    ]
    
    for filename in test_cases:
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        is_pdf = file_extension == 'pdf'
        print(f"   '{filename}' -> extension: '{file_extension}' -> is_pdf: {is_pdf}")

if __name__ == "__main__":
    test_file_extension_detection()
    test_pdf_upload_scenarios()
    
    print("\n✅ Debug script completed!")
    print("If all tests passed, the issue might be in the application logic or environment setup.")
