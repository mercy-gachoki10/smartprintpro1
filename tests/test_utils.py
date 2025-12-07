"""Tests for utility functions and helpers"""
import pytest
from app import get_vendor_service_categories, vendor_can_service_order
from models import Vendor, Order


class TestVendorServiceCategoryMapping:
    """Test vendor service category mapping functions"""
    
    def test_document_printing_mapping(self, vendor_user):
        """Test document printing maps to correct categories"""
        vendor_user.service_document_printing = True
        vendor_user.service_photos = False
        vendor_user.service_uniforms = False
        vendor_user.service_merchandise = False
        vendor_user.service_large_format = False
        
        categories = get_vendor_service_categories(vendor_user)
        
        assert "Document Printing" in categories
        assert "Flyers & Brochures" in categories
        assert "Pictures / Photos" not in categories
    
    def test_photo_printing_mapping(self, vendor_user):
        """Test photo printing maps to correct categories"""
        vendor_user.service_document_printing = False
        vendor_user.service_photos = True
        vendor_user.service_uniforms = False
        vendor_user.service_merchandise = False
        vendor_user.service_large_format = False
        
        categories = get_vendor_service_categories(vendor_user)
        
        assert "Pictures / Photos" in categories
        assert "Framing Options" in categories
        assert "Document Printing" not in categories
    
    def test_uniforms_mapping(self, vendor_user):
        """Test uniforms service maps correctly"""
        vendor_user.service_document_printing = False
        vendor_user.service_photos = False
        vendor_user.service_uniforms = True
        vendor_user.service_merchandise = False
        vendor_user.service_large_format = False
        
        categories = get_vendor_service_categories(vendor_user)
        
        assert "Uniforms" in categories
    
    def test_merchandise_mapping(self, vendor_user):
        """Test merchandise maps to correct categories"""
        vendor_user.service_document_printing = False
        vendor_user.service_photos = False
        vendor_user.service_uniforms = False
        vendor_user.service_merchandise = True
        vendor_user.service_large_format = False
        
        categories = get_vendor_service_categories(vendor_user)
        
        assert "Custom Merchandise" in categories
        assert "Packaging & Labels" in categories
    
    def test_large_format_mapping(self, vendor_user):
        """Test large format maps to correct categories"""
        vendor_user.service_document_printing = False
        vendor_user.service_photos = False
        vendor_user.service_uniforms = False
        vendor_user.service_merchandise = False
        vendor_user.service_large_format = True
        
        categories = get_vendor_service_categories(vendor_user)
        
        assert "Banners (Digital & Vinyl)" in categories
        assert "Signage" in categories
    
    def test_multiple_services_mapping(self, vendor_user):
        """Test vendor with multiple services"""
        vendor_user.service_document_printing = True
        vendor_user.service_photos = True
        vendor_user.service_uniforms = False
        vendor_user.service_merchandise = False
        vendor_user.service_large_format = False
        
        categories = get_vendor_service_categories(vendor_user)
        
        assert "Document Printing" in categories
        assert "Pictures / Photos" in categories
        assert len(categories) >= 4  # At least 4 categories from these two services


class TestVendorOrderMatching:
    """Test vendor order matching logic"""
    
    def test_vendor_can_service_matching_order(self, vendor_user, test_order):
        """Test vendor can service order in their category"""
        test_order.service_category = "Document Printing"
        vendor_user.service_document_printing = True
        
        can_service = vendor_can_service_order(vendor_user, test_order)
        assert can_service == True
    
    def test_vendor_cannot_service_non_matching_order(self, vendor_user, test_order):
        """Test vendor cannot service order outside their category"""
        test_order.service_category = "Uniforms"
        vendor_user.service_document_printing = True
        vendor_user.service_uniforms = False
        
        can_service = vendor_can_service_order(vendor_user, test_order)
        assert can_service == False
    
    def test_vendor_with_no_services_matches_nothing(self, vendor_user, test_order):
        """Test vendor with no services enabled cannot match any orders"""
        vendor_user.service_document_printing = False
        vendor_user.service_photos = False
        vendor_user.service_uniforms = False
        vendor_user.service_merchandise = False
        vendor_user.service_large_format = False
        
        test_order.service_category = "Document Printing"
        
        can_service = vendor_can_service_order(vendor_user, test_order)
        assert can_service == False


class TestFormValidation:
    """Test form validation logic"""
    
    def test_vendor_signup_sets_service_flags(self, client, db_session):
        """Test vendor signup form correctly sets service flags"""
        response = client.post('/signup', data={
            'business_name': 'Flag Test Shop',
            'email': 'flagtest@vendor.com',
            'phone': '+254722666666',
            'business_type': 'print_shop',
            'services_offered': ['document_printing', 'photo_printing', 'large_format'],
            'user_type': 'vendor',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        from models import Vendor
        vendor = Vendor.query.filter_by(email='flagtest@vendor.com').first()
        
        assert vendor is not None
        assert vendor.service_document_printing == True
        assert vendor.service_photos == True
        assert vendor.service_large_format == True
        assert vendor.service_uniforms == False
        assert vendor.service_merchandise == False
    
    def test_vendor_services_offered_human_readable(self, client, db_session):
        """Test services_offered field contains human-readable names"""
        response = client.post('/signup', data={
            'business_name': 'Readable Test Shop',
            'email': 'readable@vendor.com',
            'phone': '+254722555555',
            'business_type': 'print_shop',
            'services_offered': ['document_printing', 'photo_printing'],
            'user_type': 'vendor',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        from models import Vendor
        vendor = Vendor.query.filter_by(email='readable@vendor.com').first()
        
        # Should have human-readable names, not form values
        assert 'Document Printing' in vendor.services_offered
        assert 'Photo Printing' in vendor.services_offered
        assert 'document_printing' not in vendor.services_offered
    
    def test_vendor_business_type_human_readable(self, client, db_session):
        """Test business_type field contains human-readable name"""
        response = client.post('/signup', data={
            'business_name': 'Type Test Shop',
            'email': 'typetest@vendor.com',
            'phone': '+254722444444',
            'business_type': 'print_shop',  # Form value
            'services_offered': ['document_printing'],
            'user_type': 'vendor',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        from models import Vendor
        vendor = Vendor.query.filter_by(email='typetest@vendor.com').first()
        
        # Should be human-readable, not form value
        assert vendor.business_type == 'Print Shop'
        assert vendor.business_type != 'print_shop'


class TestHelperFunctions:
    """Test various helper functions"""
    
    def test_order_number_generation(self, test_order):
        """Test order numbers follow expected format"""
        from datetime import datetime
        
        # Should be in format ORD-YYYYMMDD-####
        assert test_order.order_number.startswith('ORD-')
        
        parts = test_order.order_number.split('-')
        assert len(parts) == 3
        
        # Check date part (YYYYMMDD)
        date_part = parts[1]
        assert len(date_part) == 8
        assert date_part.isdigit()
        
        # Check sequence part (####)
        seq_part = parts[2]
        assert len(seq_part) == 4
        assert seq_part.isdigit()
    
    def test_order_total_calculation_method(self, test_order_with_items):
        """Test order calculate_total method"""
        initial_total = test_order_with_items.total_amount
        
        # Recalculate
        calculated = test_order_with_items.calculate_total()
        
        assert calculated == initial_total
        assert calculated == test_order_with_items.base_fee + test_order_with_items.subtotal
