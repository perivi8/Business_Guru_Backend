#!/usr/bin/env python3
"""
Test Loan Status Email Updates for TMIS Business Guru
Tests the new loan status email template
"""

import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_loan_status_email():
    """Test loan status email functionality"""
    logger.info("🚀 Testing loan status email functionality...")
    
    try:
        # Import email service
        from production_email_service_enhanced import enhanced_email_service
        logger.info("✅ Enhanced email service imported successfully")
        
        # Mock client data
        mock_client_data = {
            'legal_name': 'ABC Business Solutions Pvt Ltd',
            'trade_name': 'ABC Solutions',
            'registration_number': 'REG123456789',
            'constitution_type': 'Proprietorship',
            'mobile_number': '9876543210',
            'status': 'interested',
            'loan_status': 'approved',
            'user_email': 'client@abcsolutions.com',
            'company_email': 'info@abcsolutions.com'
        }
        
        # Mock TMIS users
        mock_tmis_users = [
            {'email': 'tmis.admin@businessguru.com'},
            {'email': 'tmis.manager@businessguru.com'}
        ]
        
        # Test different loan statuses
        loan_statuses = ['approved', 'hold', 'processing', 'rejected']
        
        for loan_status in loan_statuses:
            logger.info(f"📧 Testing loan status: {loan_status}")
            
            # Test email notification
            success = enhanced_email_service.send_client_update_notification(
                client_data=mock_client_data,
                admin_name='Test Admin',
                tmis_users=mock_tmis_users,
                update_type=f'loan status {loan_status}',
                loan_status=loan_status
            )
            
            if success:
                logger.info(f"✅ Loan status {loan_status} email sent successfully")
            else:
                logger.error(f"❌ Loan status {loan_status} email failed")
                return False
        
        logger.info("🎉 All loan status email tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def test_email_templates():
    """Test email template generation"""
    logger.info("📧 Testing email template generation...")
    
    try:
        from production_email_service_enhanced import enhanced_email_service
        
        mock_client_data = {
            'legal_name': 'Test Business Ltd',
            'trade_name': 'Test Trade',
            'registration_number': 'TEST123',
            'constitution_type': 'Proprietorship',
            'mobile_number': '9876543210',
            'status': 'interested',
            'loan_status': 'approved',
            'user_email': 'test@example.com',
            'company_email': 'company@example.com'
        }
        
        # Test loan status template
        loan_template = enhanced_email_service._create_loan_status_client_email_template(
            mock_client_data, 'approved', 'Test Admin'
        )
        
        # Check if template contains expected content
        expected_content = [
            'Dear Test Business Ltd',
            'Your loan status is APPROVED by admin in TMIS Business Guru',
            'Application Details',
            'Legal Name',
            'Trade Name',
            'Registration Number',
            'Constitution Type',
            'Mobile Number'
        ]
        
        for content in expected_content:
            if content not in loan_template:
                logger.error(f"❌ Missing content in template: {content}")
                return False
        
        logger.info("✅ Loan status email template generated successfully")
        logger.info("✅ Template contains all expected content")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Template test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting loan status email tests...")
    logger.info(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Email Templates
    template_test = test_email_templates()
    if not template_test:
        logger.error("❌ Template test failed")
        return False
    
    # Test 2: Email Functionality (if SMTP configured)
    smtp_email = os.getenv('SMTP_EMAIL')
    if smtp_email:
        email_test = test_loan_status_email()
        if not email_test:
            logger.error("❌ Email functionality test failed")
            return False
    else:
        logger.info("⚠️ SMTP not configured, skipping email sending test")
    
    logger.info("🎉 All loan status email tests passed!")
    logger.info("✅ Loan status email system is ready")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ Test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Test failed")
        sys.exit(1)
