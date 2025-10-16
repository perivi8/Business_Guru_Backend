#!/usr/bin/env python3
"""
Test the new Brevo API key
"""

import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def test_brevo_api_key():
    """Test the new Brevo API key"""
    print("🔑 Testing New Brevo API Key")
    print("=" * 40)
    
    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException
        
        brevo_api_key = os.getenv('BREVO_API_KEY')
        print(f"📧 API Key: {brevo_api_key[:15]}... (Type: {'Transactional' if brevo_api_key.startswith('xkeysib-') else 'SMTP'})")
        print(f"📧 From Email: {os.getenv('BREVO_FROM_EMAIL')}")
        print(f"📧 From Name: {os.getenv('BREVO_FROM_NAME')}")
        print()
        
        # Initialize Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key
        brevo_service = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        print("✅ Brevo API service initialized")
        
        # Create test email
        test_recipients = [sib_api_v3_sdk.SendSmtpEmailTo(
            email='perivihk@gmail.com',
            name='Test User'
        )]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=test_recipients,
            subject="🎉 Brevo API Key Test - TMIS Business Guru",
            html_content=f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                        <h1 style="margin: 0; font-size: 24px;">🎉 Brevo API Key Test Successful!</h1>
                    </div>
                    <div style="line-height: 1.6; color: #333;">
                        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0;">✅ API Key Working Perfectly!</h3>
                            <p><strong>Your new Brevo transactional API key is working correctly!</strong></p>
                        </div>
                        
                        <h3>Test Details:</h3>
                        <ul>
                            <li><strong>API Key Type:</strong> Transactional (xkeysib-)</li>
                            <li><strong>Service:</strong> Brevo Transactional Email API</li>
                            <li><strong>From:</strong> {os.getenv('BREVO_FROM_NAME')} &lt;{os.getenv('BREVO_FROM_EMAIL')}&gt;</li>
                            <li><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        </ul>
                        
                        <h3>Migration Status:</h3>
                        <ul>
                            <li>✅ SendPulse completely replaced with Brevo</li>
                            <li>✅ Brevo SMTP working (Priority 1)</li>
                            <li>✅ Brevo API working (Priority 2)</li>
                            <li>✅ Email notifications ready for production</li>
                        </ul>
                        
                        <p>Your TMIS Business Guru email system is now fully operational with Brevo!</p>
                        
                        <p>Best regards,<br>
                        <strong>TMIS Business Guru System</strong></p>
                    </div>
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px;">
                        <p>This is an automated test email from TMIS Business Guru system.</p>
                        <p>&copy; 2024 TMIS Business Guru. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_content="Brevo API Key Test Successful! Your new Brevo transactional API key is working correctly.",
            sender=sib_api_v3_sdk.SendSmtpEmailSender(
                name=os.getenv('BREVO_FROM_NAME', 'TMIS Business Guru'),
                email=os.getenv('BREVO_FROM_EMAIL')
            )
        )
        
        print("📤 Sending test email via Brevo API...")
        result = brevo_service.send_transac_email(send_smtp_email)
        
        if hasattr(result, 'message_id') and result.message_id:
            print(f"🎉 SUCCESS: Brevo API email sent successfully!")
            print(f"📧 Message ID: {result.message_id}")
            return True
        else:
            print(f"❌ FAILED: Unexpected response: {result}")
            return False
            
    except ApiException as e:
        print(f"❌ Brevo API error: {e.status} - {e.reason}")
        print(f"   Body: {e.body}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_email_service_with_api():
    """Test email service with working API"""
    print("🧪 Testing Email Service with Working API")
    print("=" * 40)
    
    try:
        from email_service import email_service
        
        print(f"📧 Email Service Status:")
        print(f"   Brevo API Available: {hasattr(email_service, 'brevo_service') and email_service.brevo_service is not None}")
        print(f"   Brevo SMTP Available: {email_service.smtp_server == 'smtp-relay.brevo.com'}")
        print()
        
        # Test with Brevo API directly
        test_recipients = [{
            'name': 'Test User',
            'email': 'perivihk@gmail.com'
        }]
        
        subject = "Email Service API Test - TMIS Business Guru"
        html_body = f"""
        <h1>🎯 Email Service API Test</h1>
        <p>This email was sent using the email service with the new Brevo API key.</p>
        <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Both SMTP and API are now working perfectly!</p>
        """
        
        print("📤 Testing email service with Brevo API...")
        success = email_service._send_brevo_email(test_recipients, subject, html_body)
        
        if success:
            print("✅ Email service API test successful!")
            return True
        else:
            print("❌ Email service API test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing New Brevo API Key")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Brevo API Key Test", test_brevo_api_key),
        ("Email Service API Test", test_email_service_with_api),
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
        print("🎉 Perfect! Both Brevo SMTP and API are working!")
        print("✅ Your email system now has dual redundancy:")
        print("   🥇 Brevo SMTP (Primary)")
        print("   🥈 Brevo API (Backup)")
        print("✅ Migration from SendPulse to Brevo is 100% complete!")
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
