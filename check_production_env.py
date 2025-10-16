#!/usr/bin/env python3
"""
Check production environment configuration for email and CORS
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check all required environment variables"""
    
    print("🔍 Production Environment Check")
    print("=" * 50)
    
    # Critical environment variables
    env_vars = {
        'MONGODB_URI': os.getenv('MONGODB_URI'),
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        
        # Email configuration
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_EMAIL': os.getenv('SMTP_EMAIL'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
        
        # Brevo configuration
        'BREVO_API_KEY': os.getenv('BREVO_API_KEY'),
        'BREVO_FROM_EMAIL': os.getenv('BREVO_FROM_EMAIL'),
        'BREVO_FROM_NAME': os.getenv('BREVO_FROM_NAME'),
        
        # CORS configuration
        'ADDITIONAL_CORS_ORIGINS': os.getenv('ADDITIONAL_CORS_ORIGINS'),
        
        # Production indicators
        'RENDER': os.getenv('RENDER'),
        'VERCEL': os.getenv('VERCEL'),
    }
    
    print("\n📋 Environment Variables Status:")
    print("-" * 40)
    
    missing_vars = []
    for var_name, var_value in env_vars.items():
        if var_value:
            # Show partial value for security
            if 'PASSWORD' in var_name or 'KEY' in var_name or 'URI' in var_name:
                display_value = f"{var_value[:10]}...{var_value[-5:]}" if len(var_value) > 15 else "***"
            else:
                display_value = var_value
            print(f"✅ {var_name}: {display_value}")
        else:
            print(f"❌ {var_name}: Missing")
            missing_vars.append(var_name)
    
    print(f"\n📊 Summary:")
    print(f"   Total variables checked: {len(env_vars)}")
    print(f"   Variables set: {len(env_vars) - len(missing_vars)}")
    print(f"   Variables missing: {len(missing_vars)}")
    
    if missing_vars:
        print(f"\n⚠️ Missing Variables: {', '.join(missing_vars)}")
        
        # Provide specific guidance
        if 'BREVO_API_KEY' in missing_vars:
            print("\n💡 Brevo Configuration:")
            print("   1. Get API key from https://app.brevo.com/settings/keys/api")
            print("   2. Set BREVO_API_KEY in Render environment variables")
            print("   3. Set BREVO_FROM_EMAIL to your verified sender email")
            print("   4. Set BREVO_FROM_NAME to your sender name")
        
        if any('SMTP' in var for var in missing_vars):
            print("\n💡 SMTP Configuration (Fallback):")
            print("   1. Use Brevo SMTP: smtp-relay.brevo.com:587")
            print("   2. Set SMTP_EMAIL to your Brevo login email")
            print("   3. Set SMTP_PASSWORD to your Brevo SMTP password")
    else:
        print("\n✅ All environment variables are configured!")
    
    # Check production environment detection
    print(f"\n🌍 Environment Detection:")
    is_production = (
        os.getenv('FLASK_ENV') == 'production' or 
        os.getenv('RENDER') == 'true' or
        os.getenv('VERCEL') == '1'
    )
    print(f"   Production detected: {is_production}")
    print(f"   FLASK_ENV: {os.getenv('FLASK_ENV', 'Not set')}")
    print(f"   RENDER: {os.getenv('RENDER', 'Not set')}")
    print(f"   VERCEL: {os.getenv('VERCEL', 'Not set')}")

if __name__ == "__main__":
    check_environment()
