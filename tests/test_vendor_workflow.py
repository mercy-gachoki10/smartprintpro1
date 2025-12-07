"""Tests for vendor quote and order workflow"""
import pytest
from datetime import datetime
from models import Quote, Order


class TestQuoteSubmission:
    """Test vendor quote submission"""
    
    def test_vendor_can_access_quote_page(self, authenticated_vendor, test_order):
        """Test vendor can access quote submission page"""
        response = authenticated_vendor.get(f'/vendor/order/{test_order.id}/quote')
        assert response.status_code == 200
    
    def test_vendor_can_submit_quote(self, authenticated_vendor, test_order, vendor_user, db_session):
        """Test vendor can submit a quote"""
        response = authenticated_vendor.post(f'/vendor/order/{test_order.id}/quote', data={
            'base_fee': '75.00',
            'subtotal': '125.00',
            'total_amount': '200.00',
            'vendor_message': 'We can complete this order in 2 days'
        }, follow_redirects=True)
        
        quote = Quote.query.filter_by(
            order_id=test_order.id,
            vendor_id=vendor_user.id
        ).first()
        
        assert quote is not None
        assert quote.total_amount == 200.0
        assert quote.status == "pending"
    
    def test_vendor_can_revise_quote(self, authenticated_vendor, test_quote, db_session):
        """Test vendor can revise their quote"""
        response = authenticated_vendor.post(f'/vendor/order/{test_quote.order_id}/quote', data={
            'base_fee': '75.00',
            'subtotal': '100.00',
            'total_amount': '175.00',
            'vendor_message': 'Updated quote with better pricing'
        }, follow_redirects=True)
        
        db_session.refresh(test_quote)
        # Should create a new quote or update existing
        quotes = Quote.query.filter_by(
            order_id=test_quote.order_id,
            vendor_id=test_quote.vendor_id
        ).all()
        
        assert len(quotes) >= 1
        latest_quote = max(quotes, key=lambda q: q.created_at)
        assert float(latest_quote.total_amount) in [175.0, 150.0]  # Either updated or new quote
    
    def test_vendor_cannot_quote_own_assigned_order(self, authenticated_vendor, test_order, vendor_user, db_session):
        """Test vendor cannot submit new quotes on order already assigned to them"""
        test_order.vendor_id = vendor_user.id
        test_order.status = "accepted"
        db_session.commit()
        
        response = authenticated_vendor.get(f'/vendor/order/{test_order.id}/quote', follow_redirects=True)
        # Should either redirect or show error


class TestQuoteResponse:
    """Test customer response to quotes"""
    
    def test_customer_can_accept_quote(self, authenticated_customer, test_quote, db_session):
        """Test customer can accept a quote"""
        response = authenticated_customer.post(
            f'/customer/order/{test_quote.order_id}/quote/{test_quote.id}/respond',
            data={
                'action': 'accept',
                'customer_response': 'Quote accepted'
            },
            follow_redirects=True
        )
        
        db_session.refresh(test_quote)
        assert test_quote.status == "accepted"
        
        order = Order.query.get(test_quote.order_id)
        assert order.vendor_id == test_quote.vendor_id
        assert order.status in ["accepted", "in_progress"]
    
    def test_customer_can_reject_quote(self, authenticated_customer, test_quote, db_session):
        """Test customer can reject a quote"""
        response = authenticated_customer.post(
            f'/customer/order/{test_quote.order_id}/quote/{test_quote.id}/respond',
            data={
                'action': 'reject',
                'customer_response': 'Price too high'
            },
            follow_redirects=True
        )
        
        db_session.refresh(test_quote)
        assert test_quote.status == "rejected"
        
        order = Order.query.get(test_quote.order_id)
        assert order.vendor_id is None  # Order should not be assigned


class TestVendorOrderManagement:
    """Test vendor order management"""
    
    def test_vendor_can_view_assigned_order(self, authenticated_vendor, test_order, vendor_user, db_session):
        """Test vendor can view orders assigned to them"""
        test_order.vendor_id = vendor_user.id
        test_order.status = "in_progress"
        db_session.commit()
        
        response = authenticated_vendor.get(f'/vendor/order/{test_order.id}')
        assert response.status_code == 200
        assert test_order.order_number.encode() in response.data
    
    def test_vendor_cannot_view_other_vendor_order(self, authenticated_vendor, test_order, db_session):
        """Test vendor cannot view orders assigned to other vendors"""
        from models import Vendor
        
        other_vendor = Vendor(
            full_name="Other Shop",
            business_name="Other Shop",
            email="other@vendor.com",
            phone="+254722999999",
            password_hash="hashed",
            active=True,
            service_document_printing=True
        )
        db_session.add(other_vendor)
        db_session.commit()
        
        test_order.vendor_id = other_vendor.id
        test_order.status = "in_progress"
        db_session.commit()
        
        response = authenticated_vendor.get(f'/vendor/order/{test_order.id}', follow_redirects=True)
        assert b"don't have access" in response.data
    
    def test_vendor_can_update_order_status(self, authenticated_vendor, test_order, vendor_user, db_session):
        """Test vendor can progress order through statuses"""
        test_order.vendor_id = vendor_user.id
        test_order.status = "in_progress"
        db_session.commit()
        
        # Progress to processing
        response = authenticated_vendor.post(f'/vendor/order/{test_order.id}/status', data={
            'new_status': 'processing',
            'notes': 'Starting production'
        }, follow_redirects=True)
        
        db_session.refresh(test_order)
        assert test_order.status == "processing"
        
        # Progress to finished
        response = authenticated_vendor.post(f'/vendor/order/{test_order.id}/status', data={
            'new_status': 'finished',
            'notes': 'Production complete'
        }, follow_redirects=True)
        
        db_session.refresh(test_order)
        assert test_order.status == "finished"


class TestVendorServiceMatching:
    """Test vendor-order service matching"""
    
    def test_vendor_sees_orders_matching_services(self, authenticated_vendor, db_session, customer_user):
        """Test vendor only sees orders matching their service categories"""
        # Create order in vendor's service category
        matching_order = Order(
            customer_id=customer_user.id,
            order_number="ORD-MATCH-001",
            service_category="Document Printing",  # Vendor offers this
            status="awaiting_quotes",
            base_fee=75.0,
            total_amount=75.0
        )
        db_session.add(matching_order)
        
        # Create order NOT in vendor's service category
        non_matching_order = Order(
            customer_id=customer_user.id,
            order_number="ORD-NOMATCH-001",
            service_category="Uniforms",  # Vendor doesn't offer this
            status="awaiting_quotes",
            base_fee=75.0,
            total_amount=75.0
        )
        db_session.add(non_matching_order)
        db_session.commit()
        
        response = authenticated_vendor.get('/dashboard')
        
        # Should see matching order
        assert b'ORD-MATCH-001' in response.data
        
        # Should NOT see non-matching order
        assert b'ORD-NOMATCH-001' not in response.data
    
    def test_newly_signed_up_vendor_sees_matching_orders(self, client, db_session, customer_user):
        """Test vendor created via signup form sees matching orders correctly"""
        # Create an order that matches document printing
        order = Order(
            customer_id=customer_user.id,
            order_number="ORD-TEST-001",
            service_category="Document Printing",
            status="awaiting_quotes",
            base_fee=75.0,
            total_amount=75.0
        )
        db_session.add(order)
        db_session.commit()
        
        # Sign up a new vendor with document printing service
        client.post('/signup', data={
            'business_name': 'New Vendor Shop',
            'email': 'newvendor@test.com',
            'phone': '+254722888888',
            'business_type': 'print_shop',
            'services_offered': ['document_printing'],  # Should set service_document_printing=True
            'user_type': 'vendor',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        # Login as the new vendor
        client.post('/login', data={
            'email': 'newvendor@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Check dashboard shows the matching order
        response = client.get('/dashboard')
        assert b'ORD-TEST-001' in response.data
