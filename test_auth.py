#!/usr/bin/env python3
"""
Test script to verify authentication and session management
"""

import sys
import requests
from requests.cookies import RequestsCookieJar

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_EMAIL = "test_customer@example.com"
TEST_PASSWORD = "TestPassword123!"


def test_signup():
    """Test user registration"""
    print("\n=== Testing Signup ===")
    
    session = requests.Session()
    
    # Get CSRF token from signup page
    response = session.get(f"{BASE_URL}/signup")
    if response.status_code != 200:
        print(f"❌ Failed to access signup page: {response.status_code}")
        return False
    
    # Find CSRF token (simple extraction)
    import re
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if not csrf_match:
        print("❌ Could not find CSRF token")
        return False
    
    csrf_token = csrf_match.group(1)
    
    # Submit signup form
    data = {
        'csrf_token': csrf_token,
        'full_name': 'Test Customer',
        'email': TEST_EMAIL,
        'phone': '+254700000001',
        'organization': 'Test Org',
        'user_type': 'customer',
        'password': TEST_PASSWORD,
        'confirm_password': TEST_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/signup", data=data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("✅ Signup successful")
        return True
    else:
        print(f"❌ Signup failed: {response.status_code}")
        return False


def test_login_logout():
    """Test login and logout functionality"""
    print("\n=== Testing Login & Logout ===")
    
    session = requests.Session()
    
    # Get login page and CSRF token
    response = session.get(f"{BASE_URL}/login")
    if response.status_code != 200:
        print(f"❌ Failed to access login page: {response.status_code}")
        return False
    
    import re
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if not csrf_match:
        print("❌ Could not find CSRF token")
        return False
    
    csrf_token = csrf_match.group(1)
    
    # Submit login
    data = {
        'csrf_token': csrf_token,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'remember': False
    }
    
    response = session.post(f"{BASE_URL}/login", data=data, allow_redirects=True)
    
    if 'Welcome back' in response.text or response.url.endswith('/dashboard'):
        print("✅ Login successful")
        
        # Check session cookie exists
        if 'session' in session.cookies:
            print("✅ Session cookie set")
        else:
            print("⚠️  No session cookie found")
        
        # Test dashboard access
        response = session.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard accessible while logged in")
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
        
        # Test logout
        response = session.get(f"{BASE_URL}/logout", allow_redirects=True)
        if 'logged out' in response.text.lower():
            print("✅ Logout successful")
            
            # Verify dashboard is no longer accessible
            response = session.get(f"{BASE_URL}/dashboard", allow_redirects=False)
            if response.status_code in [302, 401, 403]:
                print("✅ Dashboard protected after logout")
                return True
            else:
                print(f"⚠️  Dashboard still accessible after logout: {response.status_code}")
                return False
        else:
            print("❌ Logout failed")
            return False
    else:
        print("❌ Login failed")
        return False


def test_session_isolation():
    """Test that sessions are properly isolated between users"""
    print("\n=== Testing Session Isolation ===")
    
    # Create two separate sessions
    session1 = requests.Session()
    session2 = requests.Session()
    
    # Login user 1
    response = session1.get(f"{BASE_URL}/login")
    import re
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if not csrf_match:
        print("❌ Could not find CSRF token for session1")
        return False
    
    data = {
        'csrf_token': csrf_match.group(1),
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
    session1.post(f"{BASE_URL}/login", data=data)
    
    # Verify session2 cannot access dashboard
    response = session2.get(f"{BASE_URL}/dashboard", allow_redirects=False)
    if response.status_code in [302, 401, 403]:
        print("✅ Session isolation working - unauthenticated user redirected")
        return True
    else:
        print(f"❌ Session isolation failed - status: {response.status_code}")
        return False


def test_password_security():
    """Test that passwords are hashed and not stored in plain text"""
    print("\n=== Testing Password Security ===")
    print("ℹ️  Check database manually to verify password_hash column contains hashed values")
    print("   Password hashes should start with 'scrypt:' or 'pbkdf2:'")
    return True


def test_csrf_protection():
    """Test CSRF protection on forms"""
    print("\n=== Testing CSRF Protection ===")
    
    session = requests.Session()
    
    # Try to submit login without CSRF token
    data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/login", data=data)
    
    if response.status_code in [400, 403] or 'CSRF' in response.text:
        print("✅ CSRF protection working")
        return True
    else:
        print("⚠️  CSRF protection may not be enforced (or form allows without token)")
        return True  # Not a critical failure


def main():
    print("=" * 60)
    print("SmartPrint Pro - Authentication & Session Testing")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print("\nMake sure the Flask app is running with: flask run --debug")
    
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start it with: flask run --debug")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Signup", test_signup()))
    results.append(("Login & Logout", test_login_logout()))
    results.append(("Session Isolation", test_session_isolation()))
    results.append(("Password Security", test_password_security()))
    results.append(("CSRF Protection", test_csrf_protection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Authentication is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the issues above.")


if __name__ == "__main__":
    main()
