#!/usr/bin/env python3
"""
Test script to verify email fallback mechanism
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_email_fallback():
    """Test email fallback mechanism"""
    print("🔍 Testing Email Fallback Mechanism")
    print("=" * 50)
    
    try:
        # Import the email service
        from email_service import EmailService
        
        # Create email service instance
        email_service = EmailService()
        
        print(f"📧 Email Service Status:")
        print(f"   Environment: {'Production' if email_service.is_production else 'Development'}")
        print(f"   SMTP Server: {email_service.smtp_server}")
        print(f"   SMTP Email: {email_service.smtp_email}")
        print(f"   Brevo Service Available: {hasattr(email_service, 'brevo_service') and email_service.brevo_service is not None}")
        print()
        
        # Create test client data
        test_client_data = {
            'legal_name': 'Test Company Ltd',
            'trade_name': 'Test Company',
            'registration_number': 'TC123456',
            'constitution_type': 'Private Limited',
            'mobile_number': '+91-9876543210',
            'status': 'hold',
            'loan_status': 'processing',
            'user_email': 'perivihk@gmail.com',
            'company_email': 'perivihk@gmail.com',
            'assigned_staff': []
        }
        
        # Create test TMIS users
        test_tmis_users = [
            {
                'name': 'Test Staff',
                'email': 'tmis.periviharikrishna@gmail.com'
            }
        ]
        
        print("📤 Testing email notification with fallback mechanism...")
        print("This will test the network connectivity and fallback to Brevo API if needed")
        print()
        
        # Test the email notification
        success = email_service.send_client_update_notification(
            client_data=test_client_data,
            admin_name="Test Admin",
            tmis_users=test_tmis_users,
            update_type="marked as hold"
        )
        
        if success:
            print("✅ Email notification test completed successfully!")
            print("The fallback mechanism is working correctly.")
        else:
            print("❌ Email notification test failed.")
            print("Check the logs above for details on what went wrong.")
            
    except Exception as e:
        print(f"💥 Error during test: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_email_fallback()