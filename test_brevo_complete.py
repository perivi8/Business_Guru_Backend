#!/usr/bin/env python3
"""
Complete test of Brevo integration with updated credentials
"""

import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def test_brevo_configuration():
    """Test Brevo configuration"""
    print("🔍 Brevo Configuration Check:")
    print("=" * 40)
    
    brevo_api_key = os.getenv('BREVO_API_KEY')
    brevo_from_email = os.getenv('BREVO_FROM_EMAIL')
    brevo_from_name = os.getenv('BREVO_FROM_NAME')
    
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    
    print(f"📧 Brevo API Configuration:")
    print(f"   API Key: {'Set' if brevo_api_key else 'Missing'} ({len(brevo_api_key) if brevo_api_key else 0} chars)")
    print(f"   From Email: {brevo_from_email}")
    print(f"   From Name: {brevo_from_name}")
    print()
    
    print(f"📧 SMTP Configuration:")
    print(f"   SMTP Email: {smtp_email}")
    print(f"   SMTP Password: {'Set' if smtp_password else 'Missing'} ({len(smtp_password) if smtp_password else 0} chars)")
    print(f"   SMTP Server: {smtp_server}")
    print(f"   SMTP Port: {smtp_port}")
    print()
    
    # Check if using Brevo SMTP
    using_brevo_smtp = smtp_server == 'smtp-relay.brevo.com'
    print(f"✅ Using Brevo SMTP: {using_brevo_smtp}")
    
    return all([brevo_api_key, brevo_from_email, smtp_email, smtp_password, smtp_server])

def test_brevo_api():
    """Test Brevo API connection"""
    print("🧪 Testing Brevo API:")
    print("-" * 30)
    
    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException
        
        brevo_api_key = os.getenv('BREVO_API_KEY')
        if not brevo_api_key:
            print("❌ Brevo API key not found")
            return False
        
        # Initialize Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key
        brevo_service = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        print("✅ Brevo API service initialized")
        
        # Test with a simple email
        test_recipients = [sib_api_v3_sdk.SendSmtpEmailTo(
            email='perivihk@gmail.com',
            name='Test User'
        )]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=test_recipients,
            subject="Brevo API Test - TMIS Business Guru",
            html_content="<h1>Brevo API Test Successful!</h1><p>Your Brevo API integration is working correctly.</p>",
            text_content="Brevo API Test Successful! Your Brevo API integration is working correctly.",
            sender=sib_api_v3_sdk.SendSmtpEmailSender(
                name=os.getenv('BREVO_FROM_NAME', 'TMIS Business Guru'),
                email=os.getenv('BREVO_FROM_EMAIL')
            )
        )
        
        print("📤 Sending test email via Brevo API...")
        result = brevo_service.send_transac_email(send_smtp_email)
        
        if hasattr(result, 'message_id') and result.message_id:
            print(f"✅ Brevo API email sent successfully! Message ID: {result.message_id}")
            return True
        else:
            print(f"❌ Brevo API email failed: {result}")
            return False
            
    except ApiException as e:
        print(f"❌ Brevo API error: {e.status} - {e.reason}")
        print(f"   Body: {e.body}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_smtp_connection():
    """Test SMTP connection"""
    print("🧪 Testing SMTP Connection:")
    print("-" * 30)
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_email = os.getenv('SMTP_EMAIL')
        smtp_password = os.getenv('SMTP_PASSWORD')
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        print(f"📧 Connecting to {smtp_server}:{smtp_port}")
        print(f"📧 Login: {smtp_email}")
        
        # Test SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()
        server.login(smtp_email, smtp_password)
        
        print("✅ SMTP connection successful!")
        
        # Send test email
        msg = MIMEMultipart('alternative')
        msg['From'] = f"TMIS Business Guru <{smtp_email}>"
        msg['To'] = 'perivihk@gmail.com'
        msg['Subject'] = "Brevo SMTP Test - TMIS Business Guru"
        
        html_content = """
        <html>
        <body>
            <h1>🎉 Brevo SMTP Test Successful!</h1>
            <p>Your Brevo SMTP configuration is working correctly.</p>
            <p><strong>Server:</strong> smtp-relay.brevo.com</p>
            <p><strong>Login:</strong> 996536001@smtp-brevo.com</p>
            <p><strong>Test Time:</strong> {}</p>
        </body>
        </html>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        text_content = "Brevo SMTP Test Successful! Your Brevo SMTP configuration is working correctly."
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        print("📤 Sending test email via Brevo SMTP...")
        server.send_message(msg)
        server.quit()
        
        print("✅ SMTP email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ SMTP error: {e}")
        return False

def test_email_service():
    """Test the integrated email service"""
    print("🧪 Testing Email Service Integration:")
    print("-" * 30)
    
    try:
        from email_service import email_service
        
        print(f"📧 Email Service Status:")
        print(f"   Environment: {'Production' if email_service.is_production else 'Development'}")
        print(f"   Brevo Available: {hasattr(email_service, 'brevo_service') and email_service.brevo_service is not None}")
        print(f"   SMTP Available: {bool(email_service.smtp_email and email_service.smtp_password)}")
        print(f"   SMTP Server: {email_service.smtp_server}")
        print(f"   Email Priority: {'Brevo' if hasattr(email_service, 'brevo_service') and email_service.brevo_service else 'SMTP'}")
        
        # Test sending via email service
        test_recipients = [{
            'name': 'Test User',
            'email': 'perivihk@gmail.com'
        }]
        
        subject = "Email Service Test - TMIS Business Guru"
        html_body = f"""
        <h1>🎉 Email Service Test Successful!</h1>
        <p>Your TMIS Business Guru email service is working correctly with Brevo.</p>
        <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Service Used:</strong> {'Brevo API' if hasattr(email_service, 'brevo_service') and email_service.brevo_service else 'Brevo SMTP'}</p>
        """
        
        print("📤 Sending test email via Email Service...")
        
        if hasattr(email_service, 'brevo_service') and email_service.brevo_service:
            success = email_service._send_brevo_email(test_recipients, subject, html_body)
            service_used = "Brevo API"
        else:
            success = email_service._send_email(['perivihk@gmail.com'], subject, html_body)
            service_used = "Brevo SMTP"
        
        if success:
            print(f"✅ Email Service test successful using {service_used}!")
            return True
        else:
            print(f"❌ Email Service test failed")
            return False
            
    except Exception as e:
        print(f"❌ Email Service error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Complete Brevo Integration Test")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Configuration Check", test_brevo_configuration),
        ("Brevo API Test", test_brevo_api),
        ("SMTP Connection Test", test_smtp_connection),
        ("Email Service Integration", test_email_service),
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
        print("🎉 All tests passed! Brevo integration is fully working!")
        print("✅ Your email notifications are ready for production!")
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
