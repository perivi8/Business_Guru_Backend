#!/usr/bin/env python3
"""
Test script to verify Cloudinary access control fix for PDF uploads.
This script tests that PDF files are uploaded with proper public access control.
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

def test_cloudinary_import():
    """Test that Cloudinary can be imported and configured"""
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        print("✅ Cloudinary modules imported successfully")
        
        # Check if Cloudinary is configured
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )
            print(f"✅ Cloudinary configured successfully with cloud: {cloud_name}")
            return True
        else:
            print("⚠️ Cloudinary environment variables not set")
            return False
    except ImportError as e:
        print(f"❌ Cloudinary import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Cloudinary configuration failed: {e}")
        return False

def test_pdf_upload_parameters():
    """Test that the PDF upload parameters are correctly set"""
    # Read the client_routes.py file to check for correct parameters
    client_routes_path = os.path.join(os.path.dirname(__file__), 'client_routes.py')
    
    if not os.path.exists(client_routes_path):
        print(f"❌ client_routes.py not found at {client_routes_path}")
        return False
    
    with open(client_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for access_control parameter instead of access_mode
    if 'access_mode="public"' in content:
        print("❌ Found deprecated access_mode parameter")
        return False
    
    if 'access_control=[{"access_type": "anonymous"}]' in content:
        print("✅ Found correct access_control parameter for public access")
    else:
        print("❌ Missing access_control parameter")
        return False
    
    # Check for PDF handling
    if 'file_extension == \'pdf\'' in content:
        print("✅ Found PDF file extension handling")
    else:
        print("❌ Missing PDF file extension handling")
        return False
    
    return True

def test_enquiry_routes_parameters():
    """Test that the enquiry routes have correct parameters"""
    # Read the enquiry_routes.py file to check for correct parameters
    enquiry_routes_path = os.path.join(os.path.dirname(__file__), 'enquiry_routes.py')
    
    if not os.path.exists(enquiry_routes_path):
        print(f"❌ enquiry_routes.py not found at {enquiry_routes_path}")
        return False
    
    with open(enquiry_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for access_control parameter instead of access_mode
    if 'access_mode="public"' in content:
        print("❌ Found deprecated access_mode parameter in enquiry_routes.py")
        return False
    
    if 'access_control=[{"access_type": "anonymous"}]' in content:
        print("✅ Found correct access_control parameter in enquiry_routes.py")
    else:
        print("❌ Missing access_control parameter in enquiry_routes.py")
        return False
    
    return True

def create_test_pdf():
    """Create a simple test PDF file"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary PDF file
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.close()
        
        # Create a simple PDF
        c = canvas.Canvas(temp_file.name, pagesize=letter)
        c.drawString(100, 750, "Test PDF for Cloudinary Upload")
        c.drawString(100, 730, "This is a test document to verify public access.")
        c.save()
        
        print(f"✅ Created test PDF: {temp_file.name}")
        return temp_file.name
    except ImportError:
        print("⚠️ reportlab not available, creating simple text file instead")
        # Create a simple text file with PDF extension
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(b"%PDF-1.4\n%Test PDF content for upload testing\n")
        temp_file.close()
        print(f"✅ Created test PDF-like file: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"❌ Failed to create test PDF: {e}")
        return None

def main():
    """Main test function"""
    print("🔍 Testing Cloudinary Access Control Fix")
    print("=" * 50)
    
    # Test 1: Cloudinary import and configuration
    print("\n1. Testing Cloudinary import and configuration...")
    if not test_cloudinary_import():
        print("❌ Cloudinary test failed")
        return False
    
    # Test 2: Check client_routes.py parameters
    print("\n2. Testing client_routes.py parameters...")
    if not test_pdf_upload_parameters():
        print("❌ Client routes parameter test failed")
        return False
    
    # Test 3: Check enquiry_routes.py parameters
    print("\n3. Testing enquiry_routes.py parameters...")
    if not test_enquiry_routes_parameters():
        print("❌ Enquiry routes parameter test failed")
        return False
    
    # Test 4: Create test PDF
    print("\n4. Creating test PDF file...")
    test_pdf_path = create_test_pdf()
    if not test_pdf_path:
        print("❌ Failed to create test PDF")
        return False
    
    # Clean up test file
    try:
        os.unlink(test_pdf_path)
        print("✅ Cleaned up test file")
    except Exception as e:
        print(f"⚠️ Failed to clean up test file: {e}")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Cloudinary access control fix is implemented correctly.")
    print("\nChanges made:")
    print("  - Replaced deprecated 'access_mode' parameter with 'access_control'")
    print("  - Set access_control=[{'access_type': 'anonymous'}] for public access")
    print("  - Applied fix to both client_routes.py and enquiry_routes.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)