"""Integration tests for complete workflows"""
import pytest
from datetime import datetime
from models import Order, Quote, Review, ServicePrice


class TestCompleteOrderWorkflow:
    """Test complete order workflow from creation to completion"""
    
    def test_full_order_lifecycle(self, client, db_session, customer_user, vendor_user):
        """Test complete order flow: create -> quote -> accept -> complete -> review"""
        
        # Step 1: Customer logs in
        client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        })
        
        # Step 2: Customer creates order
        service = ServicePrice.query.filter_by(category="Document Printing").first()
        response = client.post('/create-order', data={
            'items[1][service]': service.id,
            'items[1][quantity]': '10',
            'items[1][specifications]': 'A4, Color',
            'quote_duration': '24',
            'customer_notes': 'Need this urgently'
        })
        
        order = Order.query.filter_by(customer_id=customer_user.id).first()
        assert order is not None
        assert order.status == "pending"
        
        # Step 3: Update order status to awaiting quotes
        order.status = "awaiting_quotes"
        db_session.commit()
        
        # Step 4: Vendor logs in
        client.get('/logout')
        client.post('/login', data={
            'email': 'vendor@test.com',
            'password': 'password123'
        })
        
        # Step 5: Vendor sees order in dashboard
        response = client.get('/dashboard')
        assert order.order_number.encode() in response.data
        
        # Step 6: Vendor submits quote
        response = client.post(f'/vendor/order/{order.id}/quote', data={
            'quoted_amount': '150.00',
            'estimated_completion_hours': '48',
            'vendor_notes': 'Can complete in 2 days'
        }, follow_redirects=True)
        
        quote = Quote.query.filter_by(order_id=order.id, vendor_id=vendor_user.id).first()
        assert quote is not None
        assert quote.status == "pending"
        
        # Step 7: Customer logs back in
        client.get('/logout')
        client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        })
        
        # Step 8: Customer accepts quote
        response = client.post(
            f'/customer/order/{order.id}/quote/{quote.id}/respond',
            data={
                'action': 'accept',
                'customer_response': 'Looks good'
            },
            follow_redirects=True
        )
        
        db_session.refresh(order)
        assert order.vendor_id == vendor_user.id
        assert order.status in ["accepted", "in_progress"]
        
        # Step 9: Vendor completes order
        client.get('/logout')
        client.post('/login', data={
            'email': 'vendor@test.com',
            'password': 'password123'
        })
        
        # Progress through statuses
        client.post(f'/vendor/order/{order.id}/status', data={
            'new_status': 'processing'
        })
        client.post(f'/vendor/order/{order.id}/status', data={
            'new_status': 'finished'
        })
        client.post(f'/vendor/order/{order.id}/status', data={
            'new_status': 'ready_dispatch'
        })
        client.post(f'/vendor/order/{order.id}/status', data={
            'new_status': 'dispatched'
        })
        client.post(f'/vendor/order/{order.id}/status', data={
            'new_status': 'completed'
        })
        
        db_session.refresh(order)
        assert order.status == "completed"
        
        # Step 10: Customer leaves review
        client.get('/logout')
        client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        })
        
        response = client.post(f'/customer/order/{order.id}/review', data={
            'rating': '5',
            'comment': 'Excellent service!'
        }, follow_redirects=True)
        
        review = Review.query.filter_by(order_id=order.id).first()
        assert review is not None
        assert review.rating == 5
        assert review.vendor_id == vendor_user.id


class TestMultiVendorQuoting:
    """Test multiple vendors quoting on same order"""
    
    def test_multiple_vendors_can_quote(self, client, db_session, customer_user, vendor_user):
        """Test multiple vendors can submit quotes on same order"""
        from models import Vendor
        
        # Create second vendor
        vendor2 = Vendor(
            full_name="Second Print Shop",
            business_name="Second Print Shop",
            email="vendor2@test.com",
            phone="+254722100002",
            password_hash="$2b$12$hashedpassword",
            active=True,
            service_document_printing=True,
            service_photos=True
        )
        db_session.add(vendor2)
        db_session.commit()
        
        # Create order
        service = ServicePrice.query.filter_by(category="Document Printing").first()
        order = Order(
            customer_id=customer_user.id,
            order_number="ORD-MULTI-001",
            service_category="Document Printing",
            status="awaiting_quotes",
            base_fee=75.0,
            total_amount=75.0
        )
        db_session.add(order)
        db_session.commit()
        
        # First vendor quotes
        client.post('/login', data={
            'email': 'vendor@test.com',
            'password': 'password123'
        })
        
        client.post(f'/vendor/order/{order.id}/quote', data={
            'quoted_amount': '150.00',
            'estimated_completion_hours': '48'
        })
        
        # Second vendor quotes
        client.get('/logout')
        client.post('/login', data={
            'email': 'vendor2@test.com',
            'password': 'password123'
        })
        
        client.post(f'/vendor/order/{order.id}/quote', data={
            'quoted_amount': '140.00',
            'estimated_completion_hours': '36'
        })
        
        # Check both quotes exist
        quotes = Quote.query.filter_by(order_id=order.id).all()
        assert len(quotes) == 2
        
        # Customer should see both quotes
        client.get('/logout')
        client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        })
        
        response = client.get(f'/customer/order/{order.id}')
        assert b'150.00' in response.data or b'150' in response.data
        assert b'140.00' in response.data or b'140' in response.data


class TestVendorSignupIntegration:
    """Test vendor signup creates properly configured vendor"""
    
    def test_vendor_signup_and_order_matching(self, client, db_session, customer_user):
        """Test newly signed up vendor can see matching orders"""
        
        # Create order that should match vendor's services
        service = ServicePrice.query.filter_by(category="Document Printing").first()
        order = Order(
            customer_id=customer_user.id,
            order_number="ORD-SIGNUP-001",
            service_category="Document Printing",
            status="awaiting_quotes",
            base_fee=75.0,
            total_amount=75.0
        )
        db_session.add(order)
        db_session.commit()
        
        # Sign up new vendor
        response = client.post('/signup', data={
            'business_name': 'Integration Test Shop',
            'email': 'integration@vendor.com',
            'phone': '+254722777777',
            'business_type': 'print_shop',
            'services_offered': ['document_printing', 'photo_printing'],
            'user_type': 'vendor',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        # Verify vendor was created with correct flags
        from models import Vendor
        vendor = Vendor.query.filter_by(email='integration@vendor.com').first()
        assert vendor is not None
        assert vendor.service_document_printing == True
        assert vendor.service_photos == True
        
        # Login as new vendor
        client.post('/login', data={
            'email': 'integration@vendor.com',
            'password': 'password123'
        })
        
        # Check dashboard shows matching order
        response = client.get('/dashboard')
        assert b'ORD-SIGNUP-001' in response.data


class TestOrderFileHandling:
    """Test file upload and download for orders"""
    
    def test_order_file_upload_and_download(self, authenticated_customer, db_session):
        """Test customer can upload file and it can be downloaded"""
        # This test would require actual file handling
        # Placeholder for file upload/download testing
        pass


class TestReviewSystem:
    """Test review and rating system"""
    
    def test_customer_can_review_completed_order(self, client, db_session, customer_user, vendor_user):
        """Test customer can leave review after order completion"""
        
        # Create completed order
        order = Order(
            customer_id=customer_user.id,
            vendor_id=vendor_user.id,
            order_number="ORD-REVIEW-001",
            service_category="Document Printing",
            status="completed",
            base_fee=75.0,
            total_amount=175.0
        )
        db_session.add(order)
        db_session.commit()
        
        # Login as customer
        client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        })
        
        # Submit review
        response = client.post(f'/customer/order/{order.id}/review', data={
            'rating': '5',
            'comment': 'Great work!'
        }, follow_redirects=True)
        
        review = Review.query.filter_by(order_id=order.id).first()
        assert review is not None
        assert review.rating == 5
        assert review.vendor_id == vendor_user.id
    
    def test_vendor_average_rating_calculated(self, db_session, vendor_user, customer_user):
        """Test vendor average rating is calculated correctly"""
        from sqlalchemy import func
        
        # Create multiple completed orders with reviews
        for i, rating in enumerate([5, 4, 5, 3, 4]):
            order = Order(
                customer_id=customer_user.id,
                vendor_id=vendor_user.id,
                order_number=f"ORD-RATING-{i:03d}",
                service_category="Document Printing",
                status="completed",
                base_fee=75.0,
                total_amount=175.0
            )
            db_session.add(order)
            db_session.flush()
            
            review = Review(
                order_id=order.id,
                customer_id=customer_user.id,
                vendor_id=vendor_user.id,
                rating=rating,
                comment=f"Review {i}"
            )
            db_session.add(review)
        
        db_session.commit()
        
        # Calculate average
        avg_rating = db_session.query(func.avg(Review.rating)).filter_by(
            vendor_id=vendor_user.id
        ).scalar()
        
        assert avg_rating == 4.2  # (5+4+5+3+4)/5
