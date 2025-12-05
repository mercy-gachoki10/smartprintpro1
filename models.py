from datetime import datetime

from flask_login import UserMixin

from extension import db


class AbstractUser(UserMixin, db.Model):
    """Base fields shared by all user tables."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    organization = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_type: str | None = None

    @property
    def is_active(self) -> bool:  # used by Flask-Login
        return bool(self.active)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.email}>"

    def get_id(self) -> str:
        """Combine user type with primary key to keep identifiers unique."""

        return f"{self.user_type}:{self.id}"


class Customer(AbstractUser):
    __tablename__ = "customers"
    user_type = "customer"


class Vendor(AbstractUser):
    __tablename__ = "vendors"
    user_type = "vendor"
    
    # Vendor-specific fields
    business_name = db.Column(db.String(200), nullable=False)
    business_address = db.Column(db.String(300))
    business_type = db.Column(db.String(100))  # Print Shop, Copy Center, etc.
    services_offered = db.Column(db.Text)  # Comma-separated list or JSON
    tax_id = db.Column(db.String(50))  # Business registration/tax number
    
    # Service categories offered (checkboxes from signup)
    service_document_printing = db.Column(db.Boolean, default=False)
    service_photos = db.Column(db.Boolean, default=False)
    service_uniforms = db.Column(db.Boolean, default=False)
    service_merchandise = db.Column(db.Boolean, default=False)
    service_large_format = db.Column(db.Boolean, default=False)


class Admin(AbstractUser):
    __tablename__ = "admins"
    user_type = "admin"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"))  # Set when customer selects a quote
    selected_quote_id = db.Column(db.Integer)  # Foreign key to be added after Quote table exists
    order_number = db.Column(db.String(50), unique=True, nullable=False)  # ORD-20231201-001
    
    # Service category for matching with vendors
    service_category = db.Column(db.String(100), nullable=False)  # Document Printing, Photos, etc.
    
    # Quote deadline
    quote_deadline = db.Column(db.DateTime)  # When quotes close for this order
    quote_duration_hours = db.Column(db.Integer, default=24)  # How many hours vendors have to quote
    
    # Order status
    # pending -> awaiting_quotes -> quoted -> accepted -> in_progress -> ready -> dispatched -> completed
    status = db.Column(db.String(50), default="pending", nullable=False)
    
    # Pricing
    base_fee = db.Column(db.Float, default=75.0)  # KSh 50-100
    subtotal = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    
    # Payment tracking
    paid_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default="unpaid")  # unpaid, partial, paid
    payment_date = db.Column(db.DateTime)
    
    # Notes and communication
    customer_notes = db.Column(db.Text)
    vendor_notes = db.Column(db.Text)  # Internal vendor notes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    vendor_assigned_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime)  # When customer accepts quote
    completed_at = db.Column(db.DateTime)
    dispatched_at = db.Column(db.DateTime)
    received_at = db.Column(db.DateTime)  # When customer confirms receipt
    ready_at = db.Column(db.DateTime)  # When order is ready for dispatch
    
    # Relationships
    customer = db.relationship("Customer", backref=db.backref("orders", lazy=True))
    vendor = db.relationship("Vendor", backref=db.backref("assigned_orders", lazy=True))
    order_items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")
    quotes = db.relationship("Quote", backref="order", lazy=True, cascade="all, delete-orphan", order_by="Quote.created_at.desc()", foreign_keys="Quote.order_id")
    status_history = db.relationship("OrderStatusHistory", backref="order", lazy=True, cascade="all, delete-orphan", order_by="OrderStatusHistory.created_at.desc()")
    review = db.relationship("Review", backref="order", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.order_number}>"
    
    def calculate_total(self):
        """Calculate order total from all items"""
        self.subtotal = sum(item.total_price for item in self.order_items)
        self.total_amount = self.base_fee + self.subtotal
        return self.total_amount
    
    @property
    def latest_quote(self):
        """Get the most recent quote"""
        return self.quotes[0] if self.quotes else None
    
    @property
    def quote_count(self):
        """Count total quotes received from all vendors"""
        return len(self.quotes)
    
    @property
    def pending_quotes(self):
        """Get all pending quotes from vendors"""
        return [q for q in self.quotes if q.status == 'pending']
    
    def get_vendor_quote_count(self, vendor_id):
        """Count quotes from a specific vendor"""
        return len([q for q in self.quotes if q.vendor_id == vendor_id])
    
    @property
    def is_quote_deadline_passed(self):
        """Check if the quote deadline has passed"""
        if not self.quote_deadline:
            return False
        return datetime.utcnow() > self.quote_deadline
    
    @property
    def quotes_open(self):
        """Check if quotes are still being accepted"""
        # Quotes closed if vendor already assigned or deadline passed
        if self.vendor_id:
            return False
        if self.is_quote_deadline_passed:
            return False
        if self.status not in ['pending', 'awaiting_quotes', 'quoted']:
            return False
        return True
    
    @property
    def time_remaining_for_quotes(self):
        """Get remaining time for quotes in a human-readable format"""
        if not self.quote_deadline or self.is_quote_deadline_passed:
            return "Closed"
        
        delta = self.quote_deadline - datetime.utcnow()
        hours = delta.total_seconds() / 3600
        
        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minutes"
        elif hours < 24:
            return f"{int(hours)} hours"
        else:
            days = int(hours / 24)
            return f"{days} days"
    
    def add_status_change(self, new_status, user_id, user_type, notes=None):
        """Track status changes"""
        history = OrderStatusHistory(
            order_id=self.id,
            old_status=self.status,
            new_status=new_status,
            changed_by_id=user_id,
            changed_by_type=user_type,
            notes=notes
        )
        self.status = new_status
        db.session.add(history)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    
    # Service details
    service_category = db.Column(db.String(100), nullable=False)  # Document Printing, Photos, Uniforms, etc.
    service_type = db.Column(db.String(200), nullable=False)  # Black & White A4, Color A4, etc.
    
    # Specifications
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Price per unit in KSh
    total_price = db.Column(db.Float, nullable=False)  # quantity * unit_price
    
    # File information (if applicable)
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(50))  # pdf, docx, image
    file_size = db.Column(db.Integer)  # in bytes
    
    # Image/Document attributes
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)
    image_format = db.Column(db.String(20))
    page_count = db.Column(db.Integer)
    
    # Additional specifications
    specifications = db.Column(db.Text)  # JSON string for additional specs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<OrderItem {self.id}: {self.service_category} - {self.service_type}>"


class ServicePrice(db.Model):
    __tablename__ = "service_prices"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    service_name = db.Column(db.String(200), nullable=False)
    unit_price_min = db.Column(db.Float, nullable=False)  # Minimum price
    unit_price_max = db.Column(db.Float, nullable=False)  # Maximum price
    unit = db.Column(db.String(50), nullable=False)  # per page, per photo, per item, etc.
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ServicePrice {self.category}: {self.service_name}>"
    
    @property
    def average_price(self):
        """Return average of min and max price"""
        return (self.unit_price_min + self.unit_price_max) / 2


class PrintJob(db.Model):
    __tablename__ = "print_jobs"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # File information
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, docx, image
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    
    # Image attributes (for images only)
    image_width = db.Column(db.Integer)  # in pixels
    image_height = db.Column(db.Integer)  # in pixels
    image_format = db.Column(db.String(20))  # PNG, JPEG, etc.
    
    # Document attributes (for PDFs/DOCX)
    page_count = db.Column(db.Integer)
    
    # Job status and tracking
    status = db.Column(db.String(50), default="pending", nullable=False)  # pending, quoted, approved, printing, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship("Customer", backref=db.backref("print_jobs", lazy=True))

    def __repr__(self):
        return f"<PrintJob {self.id}: {self.title}>"


class PasswordResetRequest(db.Model):
    __tablename__ = "password_reset_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    admin_note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey("admins.id"))

    resolver = db.relationship("Admin", foreign_keys=[resolved_by])

    def mark_completed(self, admin: Admin | None = None):
        self.status = "completed"
        self.resolved_at = datetime.utcnow()
        self.resolver = admin


class Quote(db.Model):
    """Track price quotes and negotiations between vendor and customer"""
    __tablename__ = "quotes"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False)  # Which vendor submitted this quote
    quote_number = db.Column(db.Integer, nullable=False)  # Quote version from this vendor
    
    # Pricing breakdown
    base_fee = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Communication
    vendor_message = db.Column(db.Text)  # Vendor's explanation/notes to customer
    customer_response = db.Column(db.Text)  # Customer feedback on this quote
    
    # Status tracking
    status = db.Column(db.String(50), default="pending")  # pending, accepted, rejected, revised
    sent_by_vendor_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    responded_at = db.Column(db.DateTime)  # When customer responds
    
    # Item-level pricing adjustments
    quote_items = db.relationship("QuoteItem", backref="quote", lazy=True, cascade="all, delete-orphan")
    
    # Relationships
    vendor = db.relationship("Vendor", backref="quotes")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Quote {self.quote_number} from Vendor {self.vendor_id} for Order {self.order_id}>"


class QuoteItem(db.Model):
    """Individual item pricing in a quote - allows vendor to adjust prices"""
    __tablename__ = "quote_items"
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey("quotes.id"), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey("order_items.id"), nullable=False)
    
    # Adjusted pricing from vendor
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    vendor_notes = db.Column(db.Text)  # Explanation for price adjustment
    
    # Link to original order item
    order_item = db.relationship("OrderItem", backref="quote_items")
    
    def __repr__(self):
        return f"<QuoteItem {self.id} for Quote {self.quote_id}>"


class OrderStatusHistory(db.Model):
    """Track all status changes for orders"""
    __tablename__ = "order_status_history"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50), nullable=False)
    
    # Who made the change
    changed_by_id = db.Column(db.Integer, nullable=False)
    changed_by_type = db.Column(db.String(20), nullable=False)  # customer, vendor, admin
    
    notes = db.Column(db.Text)  # Optional notes about the change
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<StatusHistory: Order {self.order_id} {self.old_status} -> {self.new_status}>"
    
    @property
    def changed_by_name(self):
        """Get the name of who made the change"""
        if self.changed_by_type == "customer":
            user = db.session.get(Customer, self.changed_by_id)
        elif self.changed_by_type == "vendor":
            user = db.session.get(Vendor, self.changed_by_id)
        elif self.changed_by_type == "admin":
            user = db.session.get(Admin, self.changed_by_id)
        else:
            return "Unknown"
        
        return user.full_name if user else "Unknown"


class Review(db.Model):
    """Customer reviews for completed orders"""
    __tablename__ = "reviews"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False)
    
    # Rating (1-5 stars)
    rating = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4, or 5
    
    # Review content
    comment = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship("Customer", backref=db.backref("reviews", lazy=True))
    vendor = db.relationship("Vendor", backref=db.backref("received_reviews", lazy=True))
    
    def __repr__(self):
        return f"<Review {self.id}: Order {self.order_id} - {self.rating} stars>"


USER_MODELS = {
    "customer": Customer,
    "vendor": Vendor,
    "admin": Admin,
}


def get_user_model(user_type: str):
    return USER_MODELS.get(user_type)


def find_user_by_email(email: str):
    """Search every user table for the provided email."""

    for model in USER_MODELS.values():
        user = model.query.filter_by(email=email).first()
        if user:
            return user
    return None


def load_user_from_identity(identity: str | None):
    if not identity or ":" not in identity:
        return None

    user_type, raw_id = identity.split(":", 1)
    model = get_user_model(user_type)
    if not model:
        return None

    return db.session.get(model, int(raw_id))
