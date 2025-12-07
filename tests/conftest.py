"""Test configuration and fixtures for SmartPrint Pro"""
import os
import tempfile
import pytest
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

from app import create_app
from extension import db
from models import Customer, Vendor, Admin, Order, OrderItem, Quote, ServicePrice, Review
from config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create and configure a test application instance"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure test app
    test_config = TestingConfig
    test_config.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    test_config.TESTING = True
    test_config.WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    
    app = create_app(test_config)
    
    with app.app_context():
        db.create_all()
        # Seed service prices
        _seed_service_prices()
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for tests"""
    with app.app_context():
        # Clear all tables before each test
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            if table.name != 'service_prices':  # Don't clear service prices
                db.session.execute(table.delete())
        db.session.commit()
        yield db.session
        db.session.remove()


@pytest.fixture
def customer_user(db_session):
    """Create a test customer user"""
    customer = Customer(
        full_name="Test Customer",
        email="customer@test.com",
        phone="+254712345678",
        organization="Test Org",
        password_hash=generate_password_hash("password123"),
        active=True
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def vendor_user(db_session):
    """Create a test vendor user"""
    vendor = Vendor(
        full_name="Test Print Shop",
        business_name="Test Print Shop",
        email="vendor@test.com",
        phone="+254722100001",
        business_address="Test Address",
        business_type="Print Shop",
        services_offered="Document Printing, Photo Printing",
        password_hash=generate_password_hash("password123"),
        active=True,
        service_document_printing=True,
        service_photos=True,
        service_uniforms=False,
        service_merchandise=False,
        service_large_format=False
    )
    db_session.add(vendor)
    db_session.commit()
    return vendor


@pytest.fixture
def admin_user(db_session):
    """Create a test admin user"""
    admin = Admin(
        full_name="Test Admin",
        email="admin@test.com",
        phone="+254700000000",
        organization="SmartPrint Admin",
        password_hash=generate_password_hash("admin123"),
        active=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def test_order(db_session, customer_user):
    """Create a test order"""
    order = Order(
        customer_id=customer_user.id,
        order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-0001",
        service_category="Document Printing",
        status="pending",
        base_fee=75.0,
        subtotal=100.0,
        total_amount=175.0,
        quote_deadline=datetime.utcnow() + timedelta(hours=24),
        quote_duration_hours=24,
        customer_notes="Test order notes"
    )
    db_session.add(order)
    db_session.commit()
    return order


@pytest.fixture
def test_order_with_items(db_session, test_order):
    """Create a test order with items"""
    service = ServicePrice.query.filter_by(category="Document Printing").first()
    
    item = OrderItem(
        order_id=test_order.id,
        service_category="Document Printing",
        service_type=service.service_name,
        quantity=10,
        unit_price=service.average_price,
        total_price=service.average_price * 10,
        specifications="A4, Black & White, Double-sided"
    )
    db_session.add(item)
    db_session.commit()
    return test_order


@pytest.fixture
def test_quote(db_session, test_order, vendor_user):
    """Create a test quote"""
    quote = Quote(
        order_id=test_order.id,
        vendor_id=vendor_user.id,
        quote_number=1,
        base_fee=75.0,
        subtotal=75.0,
        total_amount=150.0,
        vendor_message="We can complete this order in 2 days",
        status="pending"
    )
    db_session.add(quote)
    db_session.commit()
    return quote


def _seed_service_prices():
    """Seed service prices for testing"""
    services = [
        ServicePrice(
            category="Document Printing",
            service_name="Black & White Printing",
            description="Standard black and white document printing",
            unit_price_min=3.0,
            unit_price_max=7.0,
            unit="per page"
        ),
        ServicePrice(
            category="Pictures / Photos",
            service_name="4×6 Photo Print",
            description="Standard 4×6 inch photo print",
            unit_price_min=15.0,
            unit_price_max=25.0,
            unit="per photo"
        ),
        ServicePrice(
            category="Uniforms",
            service_name="T-Shirt Printing",
            description="Custom t-shirt with logo printing",
            unit_price_min=400.0,
            unit_price_max=600.0,
            unit="per shirt"
        ),
        ServicePrice(
            category="Custom Merchandise",
            service_name="Branded Mugs",
            description="Custom branded ceramic mugs",
            unit_price_min=250.0,
            unit_price_max=350.0,
            unit="per mug"
        ),
        ServicePrice(
            category="Banners (Digital & Vinyl)",
            service_name="Vinyl Banner",
            description="Custom vinyl banner printing",
            unit_price_min=1200.0,
            unit_price_max=1800.0,
            unit="per sq meter"
        ),
    ]
    
    for service in services:
        existing = ServicePrice.query.filter_by(
            category=service.category,
            service_name=service.service_name
        ).first()
        if not existing:
            db.session.add(service)
    
    db.session.commit()


@pytest.fixture
def authenticated_customer(client, customer_user):
    """Log in as customer and return client"""
    with client:
        client.post('/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        yield client


@pytest.fixture
def authenticated_vendor(client, vendor_user):
    """Log in as vendor and return client"""
    with client:
        client.post('/login', data={
            'email': 'vendor@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        yield client


@pytest.fixture
def authenticated_admin(client, admin_user):
    """Log in as admin and return client"""
    with client:
        client.post('/login', data={
            'email': 'admin@test.com',
            'password': 'admin123'
        }, follow_redirects=True)
        yield client
