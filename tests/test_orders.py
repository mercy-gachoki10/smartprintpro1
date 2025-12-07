"""Tests for order management functionality"""
import pytest
import json
from datetime import datetime, timedelta
from models import Order, OrderItem, ServicePrice


class TestOrderCreation:
    """Test order creation workflow"""
    
    def test_customer_can_access_create_order_page(self, authenticated_customer):
        """Test customer can view create order page"""
        response = authenticated_customer.get('/create-order')
        assert response.status_code == 200
    
    def test_vendor_cannot_create_order(self, authenticated_vendor):
        """Test vendor cannot create orders"""
        response = authenticated_vendor.get('/create-order')
        assert response.status_code == 302 or response.status_code == 403
    
    def test_create_order_with_service(self, authenticated_customer, db_session):
        """Test creating an order with a service"""
        service = ServicePrice.query.filter_by(category="Document Printing").first()
        
        response = authenticated_customer.post('/create-order', data={
            'items[1][service]': service.id,
            'items[1][quantity]': '10',
            'items[1][specifications]': 'A4, Black & White',
            'quote_duration': '24',
            'customer_notes': 'Urgent order'
        })
        
        # Check if order was created
        order = Order.query.filter_by(service_category=service.category).first()
        assert order is not None
        assert order.customer_notes == 'Urgent order'
        assert order.quote_duration_hours == 24
    
    def test_order_has_unique_order_number(self, authenticated_customer, db_session):
        """Test each order gets unique order number"""
        service = ServicePrice.query.first()
        
        # Create first order
        authenticated_customer.post('/create-order', data={
            'items[1][service]': service.id,
            'items[1][quantity]': '5',
            'quote_duration': '24'
        })
        
        # Create second order
        authenticated_customer.post('/create-order', data={
            'items[1][service]': service.id,
            'items[1][quantity]': '3',
            'quote_duration': '24'
        })
        
        orders = Order.query.all()
        assert len(orders) >= 2
        order_numbers = [o.order_number for o in orders]
        assert len(order_numbers) == len(set(order_numbers))  # All unique


class TestOrderViewing:
    """Test order viewing functionality"""
    
    def test_customer_can_view_own_order(self, authenticated_customer, test_order_with_items):
        """Test customer can view their order details"""
        response = authenticated_customer.get(f'/customer/order/{test_order_with_items.id}')
        assert response.status_code == 200
        assert test_order_with_items.order_number.encode() in response.data
    
    def test_customer_cannot_view_others_order(self, authenticated_customer, db_session):
        """Test customer cannot view another customer's order"""
        from models import Customer
        
        # Create another customer and their order
        other_customer = Customer(
            full_name="Other Customer",
            email="other@test.com",
            phone="+254712999999",
            password_hash="hashed",
            active=True
        )
        db_session.add(other_customer)
        db_session.commit()
        
        other_order = Order(
            customer_id=other_customer.id,
            order_number="ORD-OTHER-001",
            service_category="Document Printing",
            status="pending",
            base_fee=75.0,
            total_amount=75.0
        )
        db_session.add(other_order)
        db_session.commit()
        
        response = authenticated_customer.get(f'/customer/order/{other_order.id}', follow_redirects=True)
        assert b"don't have access" in response.data
    
    def test_vendor_can_view_available_order(self, authenticated_vendor, test_order):
        """Test vendor can view orders open for quotes"""
        response = authenticated_vendor.get(f'/vendor/order/{test_order.id}')
        assert response.status_code == 200
        assert test_order.order_number.encode() in response.data


class TestOrderStatusFlow:
    """Test order status workflow"""
    
    def test_order_starts_as_pending(self, test_order):
        """Test new orders start with pending status"""
        assert test_order.status == "pending"
    
    def test_vendor_can_update_assigned_order_status(self, authenticated_vendor, test_order, vendor_user, db_session):
        """Test vendor can update status of assigned order"""
        test_order.vendor_id = vendor_user.id
        test_order.status = "in_progress"
        db_session.commit()
        
        response = authenticated_vendor.post(f'/vendor/order/{test_order.id}/status', data={
            'new_status': 'processing',
            'notes': 'Order is being processed'
        }, follow_redirects=True)
        
        db_session.refresh(test_order)
        assert test_order.status == "processing"
    
    def test_vendor_cannot_update_unassigned_order_status(self, authenticated_vendor, test_order):
        """Test vendor cannot update status of order not assigned to them"""
        response = authenticated_vendor.post(f'/vendor/order/{test_order.id}/status', data={
            'new_status': 'in_progress'
        }, follow_redirects=True)
        
        assert b"don't have access" in response.data


class TestOrderCalculations:
    """Test order pricing and calculations"""
    
    def test_order_total_includes_base_fee(self, test_order_with_items):
        """Test order total includes base fee"""
        test_order_with_items.calculate_total()
        assert test_order_with_items.total_amount >= test_order_with_items.base_fee
    
    def test_order_calculates_subtotal_from_items(self, test_order_with_items):
        """Test order subtotal calculated from items"""
        test_order_with_items.calculate_total()
        
        items_total = sum(item.total_price for item in test_order_with_items.order_items)
        assert test_order_with_items.subtotal == items_total
    
    def test_order_total_is_base_plus_subtotal(self, test_order_with_items):
        """Test total = base_fee + subtotal"""
        test_order_with_items.calculate_total()
        expected_total = test_order_with_items.base_fee + test_order_with_items.subtotal
        assert test_order_with_items.total_amount == expected_total


class TestOrderDeadlines:
    """Test quote deadline functionality"""
    
    def test_order_has_quote_deadline(self, test_order):
        """Test order has a quote deadline"""
        assert test_order.quote_deadline is not None
        assert test_order.quote_deadline > datetime.utcnow()
    
    def test_quote_deadline_based_on_duration(self, authenticated_customer, db_session):
        """Test quote deadline is set based on duration"""
        service = ServicePrice.query.first()
        
        authenticated_customer.post('/create-order', data={
            'items[1][service]': service.id,
            'items[1][quantity]': '5',
            'quote_duration': '48'  # 48 hours
        })
        
        order = Order.query.filter_by(quote_duration_hours=48).first()
        assert order is not None
        assert order.quote_deadline is not None
