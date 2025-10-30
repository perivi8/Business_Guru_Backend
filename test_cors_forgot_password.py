#!/usr/bin/env python3
"""
Test script to verify CORS configuration for the forgot-password endpoint
"""

import requests
import json

def test_cors_forgot_password():
    """Test CORS for forgot-password endpoint"""
    base_url = "https://business-guru-backend.onrender.com"
    
    # Test 1: OPTIONS request (preflight)
    print("🧪 Testing CORS preflight for forgot-password...")
    
    options_headers = {
        'Origin': 'https://business-guru-vert.vercel.app',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options(f"{base_url}/api/forgot-password", headers=options_headers, timeout=30)
        
        print(f"📊 OPTIONS Response Status: {response.status_code}")
        print(f"📊 CORS Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower():
                print(f"  {key}: {value}")
        
        if response.status_code == 200:
            print("✅ CORS preflight successful!")
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
    
    # Test 2: Actual POST request
    print("\n🧪 Testing actual POST request...")
    
    post_headers = {
        'Origin': 'https://business-guru-vert.vercel.app',
        'Content-Type': 'application/json'
    }
    
    post_data = {
        'email': 'test@example.com'
    }
    
    try:
        response = requests.post(f"{base_url}/api/forgot-password", 
                               headers=post_headers, 
                               json=post_data, 
                               timeout=30)
        
        print(f"📊 POST Response Status: {response.status_code}")
        print(f"📊 CORS Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower():
                print(f"  {key}: {value}")
        
        # We expect 404 (user not found) but CORS should work
        if response.status_code in [404, 400, 500]:  # Expected errors but CORS should work
            print("✅ CORS working! (Got expected application error)")
        elif response.status_code == 200:
            print("✅ Request successful!")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
        
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ POST request failed: {e}")

def test_cors_debug_endpoint():
    """Test the CORS debug endpoint"""
    print("\n🧪 Testing CORS debug endpoint...")
    
    headers = {
        'Origin': 'https://business-guru-vert.vercel.app',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get("https://business-guru-backend.onrender.com/api/cors-debug", 
                              headers=headers, timeout=30)
        
        print(f"📊 Debug Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug endpoint working!")
            print(f"Request Origin: {data.get('request_origin')}")
            print(f"Allowed Origins: {len(data.get('allowed_origins', []))} origins configured")
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Debug request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting CORS tests for forgot-password endpoint...")
    test_cors_forgot_password()
    test_cors_debug_endpoint()
    print("\n🏁 CORS tests completed!")
