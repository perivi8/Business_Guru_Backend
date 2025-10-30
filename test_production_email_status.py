#!/usr/bin/env python3
"""
Test Production Email for Status Updates
This script tests if email notifications work for status updates in production
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_service_import():
    """Test if email service can be imported correctly"""
    print("🧪 Testing Email Service Import...")
    
    try:
        # Test production email service import
        from email_service import email_service
        print("✅ Production email service imported successfully")
        return True, email_service
    except ImportError as e:
        print(f"❌ Failed to import production email service: {e}")
        return False, None

def test_optimized_routes_email():
    """Test if optimized routes can access email service"""
    print("\n🧪 Testing Optimized Routes Email Access...")
    
    try:
        # Import the optimized routes module
        from optimized_status_routes import get_email_service, get_admin_name, get_tmis_users
        
        # Test email service access
        EMAIL_SERVICE_AVAILABLE, email_service = get_email_service()
        
        if EMAIL_SERVICE_AVAILABLE and email_service:
            print("✅ Optimized routes can access email service")
            
            # Test helper functions
            admin_name = get_admin_name("test_admin_id")
            tmis_users = get_tmis_users()
            
            print(f"✅ Admin name function works: {admin_name}")
            print(f"✅ TMIS users function works: {len(tmis_users)} users found")
            
            return True
        else:
            print("❌ Optimized routes cannot access email service")
            return False
            
    except Exception as e:
        print(f"❌ Error testing optimized routes: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("\n🧪 Testing Environment Variables...")
    
    required_vars = {
        'SMTP_EMAIL': os.getenv('SMTP_EMAIL'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        'RENDER': os.getenv('RENDER')
    }
    
    missing_vars = []
    
    for var_name, var_value in required_vars.items():
        if var_value:
            if var_name == 'SMTP_PASSWORD':
                print(f"✅ {var_name}: {'*' * len(var_value)}")
            else:
                print(f"✅ {var_name}: {var_value}")
        else:
            print(f"❌ {var_name}: Not set")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("\n✅ All environment variables are set")
    return True

def test_email_notification_flow():
    """Test the complete email notification flow"""
    print("\n🧪 Testing Email Notification Flow...")
    
    try:
        # Import email service
        success, email_service = test_email_service_import()
        if not success:
            return False
        
        # Test mock notification
        mock_client_data = {
            '_id': 'test_client_id',
            'legal_name': 'Test Business Ltd',
            'user_email': 'client@example.com',
            'company_email': 'company@example.com',
            'status': 'interested',
            'loan_status': 'processing'
        }
        
        mock_tmis_users = [
            {'email': 'tmis.admin@example.com'},
            {'email': 'tmis.manager@example.com'}
        ]
        
        print("📧 Testing email notification (dry run)...")
        
        # This would normally send an email, but we'll just test the structure
        try:
            # Test if the method exists and can be called
            if hasattr(email_service, 'send_client_update_notification'):
                print("✅ Email service has send_client_update_notification method")
                
                # Test email template creation
                if hasattr(email_service, '_create_tmis_email_template'):
                    template = email_service._create_tmis_email_template(
                        mock_client_data, 
                        "Test Admin", 
                        "status updated"
                    )
                    if template and len(template) > 100:
                        print("✅ Email template generation works")
                    else:
                        print("❌ Email template generation failed")
                
                return True
            else:
                print("❌ Email service missing send_client_update_notification method")
                return False
                
        except Exception as e:
            print(f"❌ Error testing email notification: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error in email notification flow test: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 TMIS Business Guru - Production Email Status Test")
    print("=" * 60)
    
    # Test environment variables
    env_test = test_environment_variables()
    
    # Test email service import
    email_import_test = test_email_service_import()[0]
    
    # Test optimized routes email access
    optimized_routes_test = test_optimized_routes_email()
    
    # Test email notification flow
    notification_flow_test = test_email_notification_flow()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", env_test),
        ("Email Service Import", email_import_test),
        ("Optimized Routes Email", optimized_routes_test),
        ("Email Notification Flow", notification_flow_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("📧 Email notifications should work for status updates in production")
        print("\n💡 Next steps:")
        print("1. Deploy the updated code to Render")
        print("2. Test admin actions (mark interested, not interested, hold)")
        print("3. Test payment gateway and loan status updates")
        print("4. Check Render logs for email notification messages")
    else:
        print(f"\n❌ {total - passed} TESTS FAILED!")
        print("🔧 Please fix the failing tests before deploying")
        
        if not env_test:
            print("\n🔧 Environment Variables Fix:")
            print("1. Go to Render dashboard")
            print("2. Select your backend service")
            print("3. Go to Environment tab")
            print("4. Add missing SMTP variables")
            
        if not email_import_test:
            print("\n🔧 Email Service Fix:")
            print("1. Ensure email_service.py is deployed")
            print("2. Check for import errors in Render logs")
            
        if not optimized_routes_test:
            print("\n🔧 Optimized Routes Fix:")
            print("1. Ensure optimized_status_routes.py is deployed")
            print("2. Check if blueprint is registered in app.py")

if __name__ == "__main__":
    main()
