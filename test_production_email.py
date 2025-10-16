#!/usr/bin/env python3
"""
Test Production Email Configuration
Run this script to test if email configuration is working in production
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_configuration():
    """Test email configuration and send test email"""
    
    print("🧪 TMIS Business Guru - Production Email Test")
    print("=" * 50)
    
    # Check if we can import the production email service
    try:
        from production_email_fix import ProductionEmailService
        print("✅ Production email service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import production email service: {e}")
        return False
    
    # Initialize email service
    try:
        email_service = ProductionEmailService()
        print("✅ Email service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize email service: {e}")
        return False
    
    # Test configuration
    print("\n🔧 Testing SMTP configuration...")
    config_valid = email_service.test_email_configuration()
    
    if not config_valid:
        print("❌ SMTP configuration test failed")
        print("\n💡 Troubleshooting steps:")
        print("1. Check if all environment variables are set in Render:")
        print("   - SMTP_EMAIL")
        print("   - SMTP_PASSWORD") 
        print("   - SMTP_SERVER")
        print("   - SMTP_PORT")
        print("2. Ensure Gmail App Password is correctly generated")
        print("3. Verify 2-Factor Authentication is enabled on Gmail")
        return False
    
    print("✅ SMTP configuration test passed")
    
    # Ask for test email
    test_email = input("\nEnter email address to send test email (or press Enter to skip): ").strip()
    
    if test_email:
        print(f"\n📧 Sending test email to: {test_email}")
        email_sent = email_service.test_email_configuration(test_email)
        
        if email_sent:
            print("✅ Test email sent successfully!")
            print("📧 Check your inbox for the test email")
        else:
            print("❌ Failed to send test email")
            return False
    else:
        print("⏭️ Skipping test email")
    
    # Test client notification (mock data)
    print("\n🧪 Testing client notification email...")
    
    mock_client_data = {
        'legal_name': 'Test Business Ltd',
        'trade_name': 'Test Business',
        'mobile_number': '+91-9876543210',
        'status': 'interested',
        'loan_status': 'processing',
        'user_email': test_email if test_email else 'client@example.com',
        'company_email': None
    }
    
    mock_tmis_users = [
        {'email': 'tmis.admin@example.com'},
        {'email': 'tmis.manager@example.com'}
    ]
    
    notification_sent = email_service.send_client_update_notification(
        client_data=mock_client_data,
        admin_name='Test Admin',
        tmis_users=mock_tmis_users,
        update_type='status updated'
    )
    
    if notification_sent:
        print("✅ Client notification test passed!")
    else:
        print("❌ Client notification test failed")
        return False
    
    print("\n🎉 All email tests passed successfully!")
    print("📧 Email notifications should now work in production")
    
    return True

def check_environment_variables():
    """Check if all required environment variables are set"""
    
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'SMTP_EMAIL': os.getenv('SMTP_EMAIL'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT')
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
    
    # Check production environment indicators
    production_vars = {
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        'RENDER': os.getenv('RENDER'),
        'VERCEL': os.getenv('VERCEL')
    }
    
    print("\n🏭 Production environment indicators:")
    for var_name, var_value in production_vars.items():
        if var_value:
            print(f"✅ {var_name}: {var_value}")
        else:
            print(f"ℹ️ {var_name}: Not set")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n💡 To fix this in Render:")
        print("1. Go to your Render dashboard")
        print("2. Select your backend service")
        print("3. Go to Environment tab")
        print("4. Add the missing variables")
        print("5. Redeploy the service")
        return False
    
    print("\n✅ All required environment variables are set")
    return True

if __name__ == "__main__":
    print("🚀 Starting TMIS Business Guru Email Configuration Test")
    print()
    
    # Check environment variables first
    env_check = check_environment_variables()
    
    if not env_check:
        print("\n❌ Environment variable check failed")
        print("Please fix the missing variables before testing email functionality")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Test email configuration
    email_test = test_email_configuration()
    
    if email_test:
        print("\n🎉 SUCCESS: Email configuration is working correctly!")
        print("📧 Admin actions should now send emails in production")
    else:
        print("\n❌ FAILED: Email configuration test failed")
        print("Please check the troubleshooting steps above")
        sys.exit(1)
