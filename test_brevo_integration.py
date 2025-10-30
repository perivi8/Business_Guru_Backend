#!/usr/bin/env python3
"""
Test script to verify Brevo email integration
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_brevo_import():
    """Test if Brevo SDK can be imported"""
    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException
        print("✅ Brevo SDK imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Brevo SDK: {e}")
        print("💡 Run: pip install sib-api-v3-sdk")
        return False

def test_brevo_configuration():
    """Test if Brevo configuration is available"""
    brevo_api_key = os.getenv('BREVO_API_KEY')
    brevo_from_email = os.getenv('BREVO_FROM_EMAIL')
    brevo_from_name = os.getenv('BREVO_FROM_NAME')
    
    print(f"🔍 Brevo Configuration Check:")
    print(f"   API Key: {'Set' if brevo_api_key else 'Missing'}")
    print(f"   From Email: {brevo_from_email if brevo_from_email else 'Missing'}")
    print(f"   From Name: {brevo_from_name if brevo_from_name else 'Missing'}")
    
    if brevo_api_key and brevo_from_email:
        print("✅ Brevo configuration is complete")
        return True
    else:
        print("❌ Brevo configuration is incomplete")
        return False

def test_brevo_service_initialization():
    """Test if Brevo service can be initialized"""
    try:
        import sib_api_v3_sdk
        
        brevo_api_key = os.getenv('BREVO_API_KEY')
        if not brevo_api_key:
            print("❌ Cannot test Brevo service - API key missing")
            return False
        
        # Initialize Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key
        brevo_service = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        print("✅ Brevo service initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Brevo service: {e}")
        return False

def test_email_service_import():
    """Test if email service can be imported and uses Brevo"""
    try:
        from email_service import email_service
        
        print(f"🔍 Email Service Status:")
        print(f"   Environment: {'Production' if email_service.is_production else 'Development'}")
        print(f"   Brevo Available: {hasattr(email_service, 'brevo_service') and email_service.brevo_service is not None}")
        print(f"   SMTP Available: {bool(email_service.smtp_email and email_service.smtp_password)}")
        
        if hasattr(email_service, 'brevo_service') and email_service.brevo_service:
            print("✅ Email service is using Brevo")
            return True
        else:
            print("⚠️ Email service is not using Brevo (may use SMTP fallback)")
            return False
            
    except Exception as e:
        print(f"❌ Failed to import email service: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Brevo Email Integration")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Brevo SDK Import", test_brevo_import),
        ("Brevo Configuration", test_brevo_configuration),
        ("Brevo Service Initialization", test_brevo_service_initialization),
        ("Email Service Import", test_email_service_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Test failed with exception: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Summary:")
    print("-" * 30)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print()
    print(f"Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Brevo integration is ready.")
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
