"""Tests for authentication functionality"""
import pytest
from flask import session
from models import Customer, Vendor, Admin
from werkzeug.security import check_password_hash


class TestSignup:
    """Test user registration"""
    
    def test_signup_page_loads(self, client):
        """Test signup page is accessible"""
        response = client.get('/signup')
        assert response.status_code == 200
        assert b'Create Account' in response.data or b'Sign Up' in response.data
    
    def test_customer_signup_success(self, client, db_session):
        """Test successful customer registration"""
        response = client.post('/signup', data={
            'full_name': 'New Customer',
            'email': 'newcustomer@test.com',
            'phone': '+254712345999',
            'organization': 'Test Company',
            'user_type': 'customer',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Account created successfully' in response.data
        
        # Verify user was created in database
        customer = Customer.query.filter_by(email='newcustomer@test.com').first()
        assert customer is not None
        assert customer.full_name == 'New Customer'
        assert customer.phone == '+254712345999'
        assert check_password_hash(customer.password_hash, 'password123')
    
    def test_vendor_signup_success(self, client, db_session):
        """Test successful vendor registration with service flags"""
        response = client.post('/signup', data={
            'business_name': 'New Print Shop',
            'email': 'newvendor@test.com',
            'phone': '+254722100999',
            'business_address': '123 Test Street',
            'business_type': 'print_shop',
            'services_offered': ['document_printing', 'photo_printing'],
            'tax_id': 'TAX123456',
            'user_type': 'vendor',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify vendor was created with correct service flags
        vendor = Vendor.query.filter_by(email='newvendor@test.com').first()
        assert vendor is not None
        assert vendor.business_name == 'New Print Shop'
        assert vendor.service_document_printing == True
        assert vendor.service_photos == True
        assert vendor.service_uniforms == False
        assert 'Document Printing' in vendor.services_offered
        assert 'Photo Printing' in vendor.services_offered
        assert vendor.business_type == 'Print Shop'  # Should be human-readable
    
    def test_signup_duplicate_email(self, client, customer_user):
        """Test signup fails with duplicate email"""
        response = client.post('/signup', data={
            'full_name': 'Another User',
            'email': 'customer@test.com',  # Already exists
            'phone': '+254712345888',
            'user_type': 'customer',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert b'already registered' in response.data
    
    def test_signup_password_mismatch(self, client):
        """Test signup fails when passwords don't match"""
        response = client.post('/signup', data={
            'full_name': 'Test User',
            'email': 'test@test.com',
            'phone': '+254712345777',
            'user_type': 'customer',
            'password': 'password123',
            'confirm_password': 'different'
        }, follow_redirects=True)
        
        assert b'Passwords must match' in response.data


class TestLogin:
    """Test user login"""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Log In' in response.data or b'Login' in response.data
    
    def test_customer_login_success(self, client, customer_user):
        """Test successful customer login"""
        response = client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back' in response.data
    
    def test_vendor_login_success(self, client, vendor_user):
        """Test successful vendor login"""
        response = client.post('/login', data={
            'email': 'vendor@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back' in response.data
    
    def test_login_invalid_email(self, client):
        """Test login fails with invalid email"""
        response = client.post('/login', data={
            'email': 'nonexistent@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'Invalid email or password' in response.data
    
    def test_login_invalid_password(self, client, customer_user):
        """Test login fails with wrong password"""
        response = client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid email or password' in response.data
    
    def test_login_inactive_user(self, client, db_session, customer_user):
        """Test login fails for deactivated user"""
        customer_user.active = False
        db_session.commit()
        
        response = client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'deactivated' in response.data


class TestLogout:
    """Test user logout"""
    
    def test_logout_success(self, authenticated_customer):
        """Test successful logout"""
        response = authenticated_customer.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'logged out' in response.data
    
    def test_logout_redirects_to_home(self, authenticated_customer):
        """Test logout redirects to home page"""
        response = authenticated_customer.get('/logout')
        assert response.status_code == 302
        assert '/login' not in response.location  # Should go to home, not login


class TestAccessControl:
    """Test role-based access control"""
    
    def test_unauthenticated_dashboard_redirect(self, client):
        """Test unauthenticated user redirected from dashboard"""
        response = client.get('/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_customer_cannot_access_vendor_routes(self, authenticated_customer, test_order):
        """Test customer cannot access vendor-only routes"""
        response = authenticated_customer.get(f'/vendor/order/{test_order.id}')
        assert response.status_code == 302 or response.status_code == 403
    
    def test_vendor_cannot_access_admin_routes(self, authenticated_vendor):
        """Test vendor cannot access admin-only routes"""
        response = authenticated_vendor.get('/admin/users')
        assert response.status_code == 302 or response.status_code == 403
    
    def test_customer_can_access_own_order(self, authenticated_customer, test_order):
        """Test customer can access their own order"""
        response = authenticated_customer.get(f'/customer/order/{test_order.id}')
        assert response.status_code == 200
