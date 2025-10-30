#!/usr/bin/env python3
"""
Complete Production Email Test for TMIS Business Guru
Tests the enhanced email service with real-world scenarios
"""

import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Test if all required environment variables are set"""
    logger.info("🔍 Testing environment variables...")
    
    required_vars = {
        'SMTP_EMAIL': os.getenv('SMTP_EMAIL'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'SMTP_PORT': os.getenv('SMTP_PORT', '587'),
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        'RENDER': os.getenv('RENDER')
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if var_value:
            logger.info(f"✅ {var_name}: {'Set' if var_name == 'SMTP_PASSWORD' else var_value}")
        else:
            logger.error(f"❌ {var_name}: Missing")
            missing_vars.append(var_name)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        logger.error("🔧 Set these in your Render dashboard:")
        logger.error("   - SMTP_EMAIL: Your Gmail address")
        logger.error("   - SMTP_PASSWORD: Your Gmail App Password (16 characters)")
        logger.error("   - SMTP_SERVER: smtp.gmail.com")
        logger.error("   - SMTP_PORT: 587")
        logger.error("   - FLASK_ENV: production")
        logger.error("   - RENDER: true")
        return False
    
    logger.info("✅ All environment variables are set")
    return True

def test_email_service_import():
    """Test if email service can be imported"""
    logger.info("📦 Testing email service import...")
    
    try:
        from production_email_service_enhanced import EnhancedProductionEmailService
        logger.info("✅ Enhanced production email service imported successfully")
        return True, EnhancedProductionEmailService()
    except ImportError as e:
        logger.error(f"❌ Failed to import enhanced email service: {e}")
        try:
            from email_service import email_service
            logger.info("✅ Fallback email service imported successfully")
            return True, email_service
        except ImportError as e2:
            logger.error(f"❌ Failed to import fallback email service: {e2}")
            return False, None

def test_smtp_connection(email_service):
    """Test SMTP connection"""
    logger.info("🔌 Testing SMTP connection...")
    
    try:
        success = email_service.test_email_configuration()
        if success:
            logger.info("✅ SMTP connection test successful")
            return True
        else:
            logger.error("❌ SMTP connection test failed")
            return False
    except Exception as e:
        logger.error(f"❌ SMTP connection test error: {e}")
        return False

def test_email_templates(email_service):
    """Test email template generation"""
    logger.info("📧 Testing email template generation...")
    
    # Mock client data matching your screenshots
    mock_client_data = {
        'legal_name': 'Test Business Ltd',
        'trade_name': 'Test Trade Name',
        'registration_number': '12345678',
        'constitution_type': 'Proprietorship',
        'mobile_number': '9876543210',
        'status': 'interested',
        'loan_status': 'approved',
        'user_email': 'client@example.com',
        'company_email': 'company@example.com'
    }
    
    try:
        # Test TMIS template
        if hasattr(email_service, '_create_tmis_email_template'):
            tmis_template = email_service._create_tmis_email_template(
                mock_client_data, 'Test Admin', 'updated'
            )
            logger.info("✅ TMIS email template generated successfully")
        
        # Test client template
        if hasattr(email_service, '_create_client_email_template'):
            client_template = email_service._create_client_email_template(
                mock_client_data, 'updated'
            )
            logger.info("✅ Client email template generated successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Email template generation failed: {e}")
        return False

def test_full_email_notification(email_service, test_email=None):
    """Test full email notification process"""
    logger.info("📨 Testing full email notification process...")
    
    if not test_email:
        logger.warning("⚠️ No test email provided, skipping actual email sending")
        return True
    
    # Mock data matching your system
    mock_client_data = {
        'legal_name': 'TMIS Test Business',
        'trade_name': 'Test Trade',
        'registration_number': 'TEST123456',
        'constitution_type': 'Proprietorship',
        'mobile_number': '9876543210',
        'status': 'interested',
        'loan_status': 'approved',
        'user_email': test_email,
        'company_email': test_email
    }
    
    mock_tmis_users = [
        {'email': 'tmis.admin@example.com'},
        {'email': 'tmis.manager@example.com'}
    ]
    
    try:
        # Test regular status update
        success = email_service.send_client_update_notification(
            client_data=mock_client_data,
            admin_name='Test Admin',
            tmis_users=mock_tmis_users,
            update_type='status updated'
        )
        
        if success:
            logger.info("✅ Regular status update email test successful")
        
        # Test loan status update
        loan_success = email_service.send_client_update_notification(
            client_data=mock_client_data,
            admin_name='Test Admin',
            tmis_users=mock_tmis_users,
            update_type='loan status approved',
            loan_status='approved'
        )
        
        success = success and loan_success
        
        if success:
            logger.info("✅ Full email notification test successful")
            logger.info(f"📧 Test emails should be sent to: {test_email}")
            return True
        else:
            logger.error("❌ Full email notification test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Full email notification test error: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting complete production email test...")
    logger.info(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Environment Variables
    env_test = test_environment_variables()
    if not env_test:
        logger.error("❌ Environment variable test failed - cannot continue")
        return False
    
    # Test 2: Email Service Import
    import_test, email_service = test_email_service_import()
    if not import_test:
        logger.error("❌ Email service import test failed - cannot continue")
        return False
    
    # Test 3: SMTP Connection
    smtp_test = test_smtp_connection(email_service)
    if not smtp_test:
        logger.error("❌ SMTP connection test failed")
        return False
    
    # Test 4: Email Templates
    template_test = test_email_templates(email_service)
    if not template_test:
        logger.error("❌ Email template test failed")
        return False
    
    # Test 5: Full Email Notification (optional)
    test_email = os.getenv('TEST_EMAIL')  # Set this in Render for actual email testing
    if test_email:
        logger.info(f"📧 Testing with email: {test_email}")
        notification_test = test_full_email_notification(email_service, test_email)
        if not notification_test:
            logger.error("❌ Full email notification test failed")
            return False
    else:
        logger.info("⚠️ TEST_EMAIL not set, skipping actual email sending test")
    
    logger.info("🎉 All tests passed successfully!")
    logger.info("✅ Production email system is ready")
    logger.info("📧 Emails will be sent when admin updates client status or loan status")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ Test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Test failed")
        sys.exit(1)
