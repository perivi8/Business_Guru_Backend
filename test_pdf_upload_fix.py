#!/usr/bin/env python3
"""
Test script to verify the PDF upload fix works correctly
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Add current directory to path to import client_routes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import the upload function from client_routes
try:
    from client_routes import upload_to_cloudinary, CLOUDINARY_AVAILABLE, CLOUDINARY_ENABLED
    print("✅ Successfully imported upload_to_cloudinary function")
except ImportError as e:
    print(f"❌ Failed to import upload_to_cloudinary: {e}")
    sys.exit(1)

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
(Test PDF Upload Fix) Tj
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

def test_pdf_upload_fix():
    """Test the PDF upload fix"""
    
    print("🧪 Testing PDF upload fix...")
    print("=" * 50)
    
    if not CLOUDINARY_AVAILABLE:
        print("❌ Cloudinary not available")
        return False
        
    if not CLOUDINARY_ENABLED:
        print("❌ Cloudinary not enabled")
        return False
    
    # Create test PDF
    pdf_file_path = create_test_pdf()
    
    try:
        print(f"📄 Created test PDF: {pdf_file_path}")
        
        # Test the upload function
        with open(pdf_file_path, 'rb') as f:
            # Mock file object with filename attribute
            class MockFile:
                def __init__(self, file_obj, filename):
                    self.file_obj = file_obj
                    self.filename = filename
                    
                def read(self, *args, **kwargs):
                    return self.file_obj.read(*args, **kwargs)
                    
                def seek(self, *args, **kwargs):
                    return self.file_obj.seek(*args, **kwargs)
                    
                def __getattr__(self, name):
                    return getattr(self.file_obj, name)
            
            mock_file = MockFile(f, 'test_document.pdf')
            
            print("📤 Attempting PDF upload with fixed function...")
            result = upload_to_cloudinary(
                mock_file, 
                "test_client_123", 
                "test_document", 
                "Test Trade Name", 
                "Test Business Name"
            )
            
            print("✅ PDF upload successful!")
            print(f"   URL: {result['url']}")
            print(f"   Public ID: {result['public_id']}")
            print(f"   Format: {result['format']}")
            print(f"   Bytes: {result['bytes']}")
            print(f"   Original filename: {result['original_filename']}")
            print(f"   Storage type: {result['storage_type']}")
            
            # Clean up uploaded file
            try:
                import cloudinary.uploader
                cloudinary.uploader.destroy(result['public_id'], resource_type="raw")
                print("🧹 Cleaned up uploaded test file")
            except Exception as cleanup_error:
                print(f"⚠️ Failed to clean up: {cleanup_error}")
            
            return True
            
    except Exception as e:
        print(f"❌ PDF upload failed: {str(e)}")
        return False
        
    finally:
        # Clean up local test file
        if os.path.exists(pdf_file_path):
            os.unlink(pdf_file_path)
            print(f"🧹 Cleaned up local test file: {pdf_file_path}")

if __name__ == "__main__":
    success = test_pdf_upload_fix()
    
    if success:
        print("\n✅ PDF upload fix test PASSED!")
        print("The PDF upload issue should now be resolved.")
    else:
        print("\n❌ PDF upload fix test FAILED!")
        print("There may still be issues with the PDF upload functionality.")
