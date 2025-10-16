#!/usr/bin/env python3
"""
Test Brevo email sending functionality
"""

import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def test_brevo_email_send():
    """Test sending an email via Brevo"""
    try:
        from email_service import email_service
        
        print("🚀 Testing Brevo Email Sending")
        print("=" * 40)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check if Brevo is available
        if not hasattr(email_service, 'brevo_service') or not email_service.brevo_service:
            print("❌ Brevo service not available")
            return False
        
        print("✅ Brevo service is available")
        print(f"📧 From: {email_service.brevo_from_name} <{email_service.brevo_from_email}>")
        print()
        
        # Test email data
        test_recipients = [{
            'name': 'Test User',
            'email': 'perivihk@gmail.com'  # Using the same email as from address for testing
        }]
        
        subject = "Brevo Integration Test - TMIS Business Guru"
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ line-height: 1.6; color: #333; }}
                .success-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Brevo Integration Successful!</h1>
                </div>
                <div class="content">
                    <div class="success-box">
                        <h3>✅ Email Service Migration Complete</h3>
                        <p><strong>SendPulse → Brevo migration completed successfully!</strong></p>
                    </div>
                    
                    <h2>Migration Summary:</h2>
                    <ul>
                        <li>✅ Replaced SendPulse with Brevo API</li>
                        <li>✅ Updated requirements.txt with sib-api-v3-sdk</li>
                        <li>✅ Updated email_service.py with Brevo integration</li>
                        <li>✅ Updated app.py endpoints for Brevo</li>
                        <li>✅ Removed all SendPulse references</li>
                        <li>✅ Brevo credentials configured in .env</li>
                    </ul>
                    
                    <h3>Test Details:</h3>
                    <p><strong>Service:</strong> Brevo API (sib-api-v3-sdk)</p>
                    <p><strong>From:</strong> {email_service.brevo_from_name} &lt;{email_service.brevo_from_email}&gt;</p>
                    <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Environment:</strong> {'Production' if email_service.is_production else 'Development'}</p>
                    
                    <p>This email confirms that your Brevo email service is working correctly and ready for production use!</p>
                    
                    <p>Best regards,<br>
                    <strong>TMIS Business Guru System</strong></p>
                </div>
                <div class="footer" style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px;">
                    <p>This is an automated test email from TMIS Business Guru system.</p>
                    <p>&copy; 2024 TMIS Business Guru. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        print("📤 Sending test email via Brevo...")
        print(f"📧 To: {test_recipients[0]['email']}")
        print(f"📧 Subject: {subject}")
        print()
        
        # Send email using Brevo
        success = email_service._send_brevo_email(test_recipients, subject, html_body)
        
        if success:
            print("🎉 SUCCESS: Brevo email sent successfully!")
            print("✅ Brevo integration is working perfectly!")
            print()
            print("📋 Next Steps:")
            print("   1. Check your email inbox for the test message")
            print("   2. Brevo is now ready for production use")
            print("   3. All email notifications will use Brevo API")
            return True
        else:
            print("❌ FAILED: Brevo email sending failed")
            print("💡 Check Brevo API credentials and configuration")
            return False
            
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_brevo_email_send()
    exit(0 if success else 1)
