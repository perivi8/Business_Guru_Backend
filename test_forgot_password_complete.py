#!/usr/bin/env python3
"""
Complete test script for forgot-password endpoint with CORS and email functionality
"""

import requests
import json
import time

def test_cors_forgot_password():
    """Test CORS for forgot-password endpoint"""
    base_url = "https://business-guru-backend.onrender.com"
    
    print("🚀 Testing Forgot Password Endpoint with CORS")
    print("=" * 60)
    
    # Test 1: OPTIONS request (preflight)
    print("\n🧪 Test 1: CORS Preflight (OPTIONS)")
    print("-" * 40)
    
    options_headers = {
        'Origin': 'https://business-guru-vert.vercel.app',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type, Authorization'
    }
    
    try:
        response = requests.options(f"{base_url}/api/forgot-password", headers=options_headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 CORS Headers:")
        cors_headers = {}
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'cors' in key.lower():
                cors_headers[key] = value
                print(f"  {key}: {value}")
        
        if response.status_code == 200 and cors_headers:
            print("✅ CORS preflight PASSED")
        else:
            print("❌ CORS preflight FAILED")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
    
    # Test 2: Actual POST request with test email
    print("\n🧪 Test 2: Actual POST Request")
    print("-" * 40)
    
    post_headers = {
        'Origin': 'https://business-guru-vert.vercel.app',
        'Content-Type': 'application/json'
    }
    
    post_data = {
        'email': 'test@example.com'  # This should fail with "Email not found" but CORS should work
    }
    
    try:
        response = requests.post(f"{base_url}/api/forgot-password", 
                               headers=post_headers, 
                               json=post_data, 
                               timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 CORS Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower():
                print(f"  {key}: {value}")
        
        print(f"📊 Response Body: {response.text}")
        
        # We expect 404 (user not found) but CORS should work
        if 'access-control-allow-origin' in response.headers:
            print("✅ CORS headers present in response")
        else:
            print("❌ CORS headers missing in response")
        
        if response.status_code in [404, 400]:
            print("✅ Expected application error (CORS working)")
        elif response.status_code == 200:
            print("✅ Unexpected success (but CORS working)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ POST request failed: {e}")

def test_cors_debug_endpoint():
    """Test the CORS debug endpoint"""
    print("\n🧪 Test 3: CORS Debug Endpoint")
    print("-" * 40)
    
    headers = {
        'Origin': 'https://business-guru-vert.vercel.app',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get("https://business-guru-backend.onrender.com/api/cors-debug", 
                              headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug endpoint working!")
            print(f"Request Origin: {data.get('request_origin')}")
            print(f"Allowed Origins: {len(data.get('allowed_origins', []))} origins configured")
            print(f"Flask Environment: {data.get('flask_env', 'Unknown')}")
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug request failed: {e}")

def test_health_endpoint():
    """Test basic health endpoint"""
    print("\n🧪 Test 4: Health Check")
    print("-" * 40)
    
    try:
        response = requests.get("https://business-guru-backend.onrender.com/api/health", timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Complete Forgot Password Tests...")
    print(f"🕒 Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_health_endpoint()
    test_cors_debug_endpoint()
    test_cors_forgot_password()
    
    print("\n🏁 All tests completed!")
    print("\n💡 If CORS is still failing:")
    print("1. Check that backend is deployed with latest changes")
    print("2. Verify environment variables are set in Render")
    print("3. Check Render logs for CORS debug messages")
    print("4. Ensure frontend origin matches exactly")
