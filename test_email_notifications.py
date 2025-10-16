#!/usr/bin/env python3
"""
Test Email Notifications for TMIS Business Guru
This script tests if email notifications work correctly in both local and production environments.
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
        # Test email service import
        from email_service import email_service
        print("✅ Email service imported successfully")
        return True, email_service
    except ImportError as e:
        print(f"❌ Failed to import email service: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error importing email service: {e}")
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
            return True
        else:
            print("❌ Optimized routes cannot access email service")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import optimized status routes: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing optimized routes: {e}")
        return False

def test_email_configuration():
    """Test email configuration"""
    print("\n🧪 Testing Email Configuration...")
    
    try:
        # Import email service
        success, email_service = test_email_service_import()
        
        if not success or not email_service:
            print("❌ Cannot test email configuration without email service")
            return False
        
        # Check if we're in production
        is_production = (
            os.getenv('FLASK_ENV') == 'production' or 
            os.getenv('RENDER') == 'true' or
            os.getenv('VERCEL') == '1'
        )
        
        print(f"Environment: {'Production' if is_production else 'Development'}")
        
        # Test configuration
        if hasattr(email_service, 'is_production'):
            print(f"Email service environment: {'Production' if email_service.is_production else 'Development'}")
        
        # Check SMTP configuration
        if hasattr(email_service, 'smtp_email'):
            print(f"SMTP Email: {email_service.smtp_email}")
        
        if hasattr(email_service, 'smtp_server'):
            print(f"SMTP Server: {email_service.smtp_server}:{getattr(email_service, 'smtp_port', 'N/A')}")
        
        # Test if required environment variables are set
        required_vars = ['SMTP_EMAIL', 'SMTP_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("\n💡 To fix this:")
            print("1. Set the missing environment variables in your .env file (for local) or Render dashboard (for production)")
            print("2. Required variables:")
            for var in required_vars:
                print(f"   - {var}")
            return False
        else:
            print("✅ All required environment variables are set")
            return True
            
    except Exception as e:
        print(f"❌ Error testing email configuration: {e}")
        return False

def test_send_email():
    """Test sending an email"""
    print("\n🧪 Testing Email Sending...")
    
    try:
        # Import email service
        success, email_service = test_email_service_import()
        
        if not success or not email_service:
            print("❌ Cannot test email sending without email service")
            return False
        
        # Get test email address
        test_email = input("Enter email address to send test email (or press Enter to skip): ").strip()
        
        if not test_email:
            print("⏭️ Skipping email sending test")
            return True
        
        # Create mock client data
        mock_client_data = {
            'legal_name': 'Test Business Ltd',
            'trade_name': 'Test Business',
            'mobile_number': '+91-9876543210',
            'status': 'interested',
            'loan_status': 'processing',
            'user_email': test_email,
            'company_email': None
        }
        
        mock_tmis_users = [
            {'email': 'tmis.admin@example.com'},
            {'email': 'tmis.manager@example.com'}
        ]
        
        # Send test email
        print(f"📧 Sending test email notification...")
        email_sent = email_service.send_client_update_notification(
            client_data=mock_client_data,
            admin_name='Test Admin',
            tmis_users=mock_tmis_users,
            update_type="test notification"
        )
        
        if email_sent:
            print("✅ Test email sent successfully!")
            print("📧 Check your inbox for the test email")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting TMIS Business Guru Email Notification Test")
    print("=" * 60)
    
    # Test 1: Email service import
    email_import_success, _ = test_email_service_import()
    if not email_import_success:
        print("\n❌ Email service import test failed")
        sys.exit(1)
    
    # Test 2: Optimized routes email access
    routes_success = test_optimized_routes_email()
    if not routes_success:
        print("\n❌ Optimized routes email access test failed")
        sys.exit(1)
    
    # Test 3: Email configuration
    config_success = test_email_configuration()
    if not config_success:
        print("\n❌ Email configuration test failed")
        sys.exit(1)
    
    # Test 4: Send email (optional)
    send_success = test_send_email()
    if not send_success:
        print("\n❌ Email sending test failed")
        # Don't exit here as this might be due to network issues
    
    print("\n" + "=" * 60)
    print("🎉 Email Notification Test Summary:")
    print(f"   ✅ Email Service Import: {'PASS' if email_import_success else 'FAIL'}")
    print(f"   ✅ Optimized Routes Access: {'PASS' if routes_success else 'FAIL'}")
    print(f"   ✅ Email Configuration: {'PASS' if config_success else 'FAIL'}")
    print(f"   ✅ Email Sending: {'PASS' if send_success else 'FAIL (optional)'}")
    
    if email_import_success and routes_success and config_success:
        print("\n🎉 SUCCESS: Email notifications should work correctly!")
        print("📧 Admin actions should now send emails in both local and production environments")
    else:
        print("\n❌ FAILED: Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()