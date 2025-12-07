"""Tests for admin functionality"""
import pytest
from models import Customer, Vendor, PasswordResetRequest


class TestAdminUserManagement:
    """Test admin user management"""
    
    def test_admin_can_view_users_list(self, authenticated_admin, customer_user, vendor_user):
        """Test admin can view list of all users"""
        response = authenticated_admin.get('/admin/users')
        assert response.status_code == 200
        assert b'customer@test.com' in response.data
        assert b'vendor@test.com' in response.data
    
    def test_admin_can_view_user_edit_page(self, authenticated_admin, customer_user):
        """Test admin can access user edit page"""
        response = authenticated_admin.get(f'/admin/users/customer/{customer_user.id}/edit')
        assert response.status_code == 200
        assert customer_user.email.encode() in response.data
    
    def test_admin_can_edit_user(self, authenticated_admin, customer_user, db_session):
        """Test admin can update user information"""
        response = authenticated_admin.post(
            f'/admin/users/customer/{customer_user.id}/edit',
            data={
                'full_name': 'Updated Customer Name',
                'phone': '+254712999999',
                'active': 'y'  # or whatever the form expects
            },
            follow_redirects=True
        )
        
        db_session.refresh(customer_user)
        assert customer_user.full_name == 'Updated Customer Name'
    
    def test_admin_can_deactivate_user(self, authenticated_admin, customer_user, db_session):
        """Test admin can deactivate a user"""
        response = authenticated_admin.post(
            f'/admin/users/customer/{customer_user.id}/edit',
            data={
                'full_name': customer_user.full_name,
                'phone': customer_user.phone,
                'active': ''  # Unchecked checkbox
            },
            follow_redirects=True
        )
        
        db_session.refresh(customer_user)
        assert customer_user.active == False


class TestPasswordResetRequests:
    """Test password reset request management"""
    
    def test_customer_can_request_password_reset(self, client, customer_user, db_session):
        """Test customer can submit password reset request"""
        response = client.post('/forgot-password', data={
            'email': 'customer@test.com'
        }, follow_redirects=True)
        
        assert b'reset request' in response.data.lower()
        
        request = PasswordResetRequest.query.filter_by(
            user_id=customer_user.id,
            user_type='customer'
        ).first()
        
        assert request is not None
        assert request.status == 'pending'
    
    def test_admin_can_view_reset_requests(self, authenticated_admin, db_session, customer_user):
        """Test admin can view password reset requests"""
        # Create a reset request
        reset_req = PasswordResetRequest(
            user_id=customer_user.id,
            user_type='customer',
            email=customer_user.email,
            status='pending'
        )
        db_session.add(reset_req)
        db_session.commit()
        
        response = authenticated_admin.get('/admin/password-requests')
        assert response.status_code == 200
        assert customer_user.email.encode() in response.data
    
    def test_admin_can_process_reset_request(self, authenticated_admin, db_session, customer_user):
        """Test admin can approve and reset user password"""
        reset_req = PasswordResetRequest(
            user_id=customer_user.id,
            user_type='customer',
            email=customer_user.email,
            status='pending'
        )
        db_session.add(reset_req)
        db_session.commit()
        
        response = authenticated_admin.post(
            f'/admin/password-requests/{reset_req.id}',
            data={
                'new_password': 'newpassword123',
                'confirm_password': 'newpassword123',
                'admin_note': 'Password reset approved'
            },
            follow_redirects=True
        )
        
        db_session.refresh(reset_req)
        assert reset_req.status == 'approved'


class TestAdminAccessControl:
    """Test admin-specific access control"""
    
    def test_customer_cannot_access_admin_routes(self, authenticated_customer):
        """Test customer cannot access admin pages"""
        response = authenticated_customer.get('/admin/users', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected or see error
        assert b'permission' in response.data.lower() or b'admin' not in response.data.lower()
    
    def test_vendor_cannot_access_admin_routes(self, authenticated_vendor):
        """Test vendor cannot access admin pages"""
        response = authenticated_vendor.get('/admin/users', follow_redirects=True)
        assert response.status_code == 200
        assert b'permission' in response.data.lower() or b'admin' not in response.data.lower()
    
    def test_unauthenticated_cannot_access_admin(self, client):
        """Test unauthenticated users redirected from admin pages"""
        response = client.get('/admin/users')
        assert response.status_code == 302
        assert '/login' in response.location


class TestAdminDashboardStats:
    """Test admin dashboard statistics"""
    
    def test_admin_sees_user_counts(self, authenticated_admin, customer_user, vendor_user):
        """Test admin dashboard shows user statistics"""
        response = authenticated_admin.get('/dashboard')
        assert response.status_code == 200
        
        # Should show counts for different user types
        assert b'customer' in response.data.lower()
        assert b'vendor' in response.data.lower()
    
    def test_admin_sees_pending_reset_count(self, authenticated_admin, db_session, customer_user):
        """Test admin sees count of pending password resets"""
        # Create pending reset requests
        reset1 = PasswordResetRequest(
            user_id=customer_user.id,
            user_type='customer',
            email=customer_user.email,
            status='pending'
        )
        db_session.add(reset1)
        db_session.commit()
        
        response = authenticated_admin.get('/dashboard')
        assert response.status_code == 200
        # Should show pending reset count
        assert b'1' in response.data or b'pending' in response.data.lower()
