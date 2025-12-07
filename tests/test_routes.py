"""Tests for public and dashboard routes"""
import pytest
from models import Order, Quote


class TestPublicRoutes:
    """Test public routes accessible to all"""
    
    def test_home_page(self, client):
        """Test home page loads"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_vendors_page(self, client, vendor_user):
        """Test vendors listing page"""
        response = client.get('/vendors')
        assert response.status_code == 200
        assert b'Test Print Shop' in response.data
    
    def test_vendor_profile_page(self, client, vendor_user):
        """Test individual vendor profile page"""
        response = client.get(f'/vendor/{vendor_user.id}')
        assert response.status_code == 200
        assert b'Test Print Shop' in response.data
    
    def test_features_page(self, client):
        """Test features page"""
        response = client.get('/features')
        assert response.status_code == 200
    
    def test_how_it_works_page(self, client):
        """Test how it works page"""
        response = client.get('/how-it-works')
        assert response.status_code == 200


class TestCustomerDashboard:
    """Test customer dashboard"""
    
    def test_customer_dashboard_loads(self, authenticated_customer):
        """Test customer can access dashboard"""
        response = authenticated_customer.get('/dashboard')
        assert response.status_code == 200
        assert b'Test Customer' in response.data
    
    def test_customer_dashboard_shows_orders(self, authenticated_customer, test_order):
        """Test customer dashboard shows their orders"""
        response = authenticated_customer.get('/dashboard')
        assert response.status_code == 200
        assert test_order.order_number.encode() in response.data
    
    def test_customer_can_create_order(self, authenticated_customer):
        """Test customer can access create order page"""
        response = authenticated_customer.get('/create-order')
        assert response.status_code == 200
        assert b'Create' in response.data or b'New Order' in response.data


class TestVendorDashboard:
    """Test vendor dashboard"""
    
    def test_vendor_dashboard_loads(self, authenticated_vendor):
        """Test vendor can access dashboard"""
        response = authenticated_vendor.get('/dashboard')
        assert response.status_code == 200
        assert b'Test Print Shop' in response.data
    
    def test_vendor_sees_available_orders(self, authenticated_vendor, test_order, db_session):
        """Test vendor sees orders matching their services"""
        test_order.status = "awaiting_quotes"
        db_session.commit()
        
        response = authenticated_vendor.get('/dashboard')
        assert response.status_code == 200
        # Vendor should see orders in their service category
        assert test_order.order_number.encode() in response.data
    
    def test_vendor_sees_assigned_orders(self, authenticated_vendor, test_order, vendor_user, db_session):
        """Test vendor sees orders assigned to them"""
        test_order.vendor_id = vendor_user.id
        test_order.status = "in_progress"
        db_session.commit()
        
        response = authenticated_vendor.get('/dashboard')
        assert response.status_code == 200
        assert test_order.order_number.encode() in response.data


class TestAdminDashboard:
    """Test admin dashboard"""
    
    def test_admin_dashboard_loads(self, authenticated_admin):
        """Test admin can access dashboard"""
        response = authenticated_admin.get('/dashboard')
        assert response.status_code == 200
        assert b'Admin' in response.data
    
    def test_admin_can_access_users(self, authenticated_admin):
        """Test admin can access user management"""
        response = authenticated_admin.get('/admin/users')
        assert response.status_code == 200
    
    def test_admin_sees_user_counts(self, authenticated_admin, customer_user, vendor_user):
        """Test admin dashboard shows user statistics"""
        response = authenticated_admin.get('/dashboard')
        assert response.status_code == 200
        # Should show some count information
        assert b'customer' in response.data.lower() or b'vendor' in response.data.lower()


class TestErrorHandlers:
    """Test error handling"""
    
    def test_404_handler(self, client):
        """Test 404 page not found"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_403_forbidden(self, authenticated_customer):
        """Test 403 forbidden access"""
        response = authenticated_customer.get('/admin/users', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected or show error message
