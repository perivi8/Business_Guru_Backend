#!/usr/bin/env python3
"""
Test environment variables loading
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("🔍 Environment Variables Check:")
print(f"   BREVO_API_KEY: {'Set' if os.getenv('BREVO_API_KEY') else 'Missing'}")
print(f"   BREVO_FROM_EMAIL: {os.getenv('BREVO_FROM_EMAIL')}")
print(f"   BREVO_FROM_NAME: {os.getenv('BREVO_FROM_NAME')}")

# Test Brevo service initialization
try:
    import sib_api_v3_sdk
    
    brevo_api_key = os.getenv('BREVO_API_KEY')
    if brevo_api_key:
        print("✅ Brevo API key found, testing initialization...")
        
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key
        brevo_service = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        print("✅ Brevo service initialized successfully!")
        
        # Test email service
        from email_service import email_service
        print(f"📧 Email service Brevo status: {hasattr(email_service, 'brevo_service') and email_service.brevo_service is not None}")
        
    else:
        print("❌ Brevo API key not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
