#!/usr/bin/env python3
"""
Verification script for Cloudinary PDF access control fix.
This script checks that the code changes have been properly implemented.
"""

import os
import sys
import re

def check_file_for_correct_parameters(file_path, function_name):
    """Check if a file contains the correct Cloudinary parameters"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that access_mode is NOT used (deprecated)
    if 'access_mode=' in content:
        print(f"❌ Found deprecated 'access_mode' parameter in {file_path}")
        return False
    
    # Check that access_control is used (correct)
    if 'access_control=[{"access_type": "anonymous"}]' in content:
        print(f"✅ Found correct 'access_control' parameter in {file_path}")
    else:
        print(f"❌ Missing 'access_control' parameter in {file_path}")
        return False
    
    # Check that invalidate is used
    if 'invalidate=True' in content:
        print(f"✅ Found 'invalidate=True' parameter in {file_path}")
    else:
        print(f"❌ Missing 'invalidate=True' parameter in {file_path}")
        return False
    
    # Check resource_type for PDF handling
    if 'resource_type="auto"' in content and 'resource_type="raw"' in content:
        print(f"✅ Found correct resource_type parameters in {file_path}")
    else:
        print(f"❌ Missing proper resource_type parameters in {file_path}")
        return False
    
    return True

def main():
    """Main verification function"""
    print("🔍 Verifying Cloudinary PDF Access Control Fix")
    print("=" * 50)
    
    # Files to check
    files_to_check = [
        ('enquiry_routes.py', 'upload_to_cloudinary_enquiry'),
        ('client_routes.py', 'upload_to_cloudinary'),
        ('client_routes.py', 'copy_business_document_to_client_folder')
    ]
    
    backend_path = os.path.dirname(__file__)
    all_passed = True
    
    for file_name, function_name in files_to_check:
        file_path = os.path.join(backend_path, file_name)
        print(f"\nChecking {file_name}...")
        if not check_file_for_correct_parameters(file_path, function_name):
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All verification checks passed!")
        print("\nNext steps:")
        print("1. Log in to your Cloudinary account")
        print("2. Go to Settings > Security")
        print("3. Enable 'Allow delivery of PDF and ZIP files'")
        print("4. Save the settings")
        print("5. Test uploading a PDF through the public enquiry form")
    else:
        print("❌ Some verification checks failed!")
        print("Please review the errors above and fix the code.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)