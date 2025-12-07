"""Tests for database models"""
import pytest
from datetime import datetime, timedelta
from models import Customer, Vendor, Order, OrderItem, Quote, Review, ServicePrice


class TestCustomerModel:
    """Test Customer model"""
    
    def test_create_customer(self, db_session):
        """Test creating a customer"""
        customer = Customer(
            full_name="John Doe",
            email="john@test.com",
            phone="+254712345678",
            password_hash="hashed",
            active=True
        )
        db_session.add(customer)
        db_session.commit()
        
        assert customer.id is not None
        assert customer.user_type == "customer"
        assert customer.is_active == True
    
    def test_customer_get_id(self, customer_user):
        """Test customer get_id method for Flask-Login"""
        user_id = customer_user.get_id()
        assert user_id == f"customer:{customer_user.id}"


class TestVendorModel:
    """Test Vendor model"""
    
    def test_create_vendor(self, db_session):
        """Test creating a vendor"""
        vendor = Vendor(
            full_name="Print Shop",
            business_name="Print Shop",
            email="shop@test.com",
            phone="+254722100001",
            password_hash="hashed",
            service_document_printing=True,
            service_photos=False,
            active=True
        )
        db_session.add(vendor)
        db_session.commit()
        
        assert vendor.id is not None
        assert vendor.user_type == "vendor"
        assert vendor.service_document_printing == True
        assert vendor.service_photos == False
    
    def test_vendor_service_flags(self, vendor_user):
        """Test vendor service category flags"""
        assert vendor_user.service_document_printing == True
        assert vendor_user.service_photos == True
        assert vendor_user.service_uniforms == False


class TestOrderModel:
    """Test Order model"""
    
    def test_create_order(self, db_session, customer_user):
        """Test creating an order"""
        order = Order(
            customer_id=customer_user.id,
            order_number="ORD-20231201-0001",
            service_category="Document Printing",
            status="pending",
            base_fee=75.0,
            subtotal=0.0,
            total_amount=75.0
        )
        db_session.add(order)
        db_session.commit()
        
        assert order.id is not None
        assert order.customer_id == customer_user.id
        assert order.status == "pending"
    
    def test_order_calculate_total(self, test_order_with_items):
        """Test order total calculation"""
        test_order_with_items.calculate_total()
        
        # Should have base_fee + subtotal
        assert test_order_with_items.subtotal > 0
        assert test_order_with_items.total_amount == test_order_with_items.base_fee + test_order_with_items.subtotal
    
    def test_order_relationships(self, test_order_with_items, customer_user):
        """Test order relationships"""
        assert test_order_with_items.customer == customer_user
        assert len(test_order_with_items.order_items) > 0


class TestQuoteModel:
    """Test Quote model"""
    
    def test_create_quote(self, db_session, test_order, vendor_user):
        """Test creating a quote"""
        quote = Quote(
            order_id=test_order.id,
            vendor_id=vendor_user.id,
            quote_number=1,
            base_fee=75.0,
            subtotal=75.0,
            total_amount=150.0,
            vendor_message="We can complete this quickly",
            status="pending"
        )
        db_session.add(quote)
        db_session.commit()
        
        assert quote.id is not None
        assert quote.order_id == test_order.id
        assert quote.vendor_id == vendor_user.id
        assert quote.status == "pending"
    
    def test_quote_relationships(self, test_quote, test_order, vendor_user):
        """Test quote relationships"""
        assert test_quote.order == test_order
        assert test_quote.vendor == vendor_user


class TestServicePriceModel:
    """Test ServicePrice model"""
    
    def test_service_prices_seeded(self, db_session):
        """Test that service prices are seeded"""
        services = ServicePrice.query.all()
        assert len(services) >= 5
        
        doc_service = ServicePrice.query.filter_by(category="Document Printing").first()
        assert doc_service is not None
        assert doc_service.average_price > 0


class TestReviewModel:
    """Test Review model"""
    
    def test_create_review(self, db_session, test_order, vendor_user):
        """Test creating a review"""
        # Assign vendor to order first
        test_order.vendor_id = vendor_user.id
        test_order.status = "completed"
        db_session.commit()
        
        review = Review(
            order_id=test_order.id,
            customer_id=test_order.customer_id,
            vendor_id=vendor_user.id,
            rating=5,
            comment="Excellent service!"
        )
        db_session.add(review)
        db_session.commit()
        
        assert review.id is not None
        assert review.rating == 5
        assert review.vendor_id == vendor_user.id
