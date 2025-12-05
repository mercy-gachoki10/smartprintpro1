# SmartPrint Pro - Developer Guide

## Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [Database Schema](#database-schema)
3. [Vendor-Customer Workflow Implementation](#vendor-customer-workflow-implementation)
4. [Testing Guide](#testing-guide)
5. [API Routes](#api-routes)
6. [Forms Reference](#forms-reference)
7. [Troubleshooting](#troubleshooting)

---

## Setup Instructions

### Windows Setup

#### Prerequisites
- Windows 10/11
- Python 3.11+ added to PATH
- PowerShell (recommended) or Command Prompt

#### Step-by-Step

**1. Clone Repository**
```powershell
git clone <your-repo-url> smartprintpro
cd smartprintpro
```

**2. Create Virtual Environment**
```powershell
python -m venv venv
```

**3. Activate Virtual Environment**
```powershell
./venv/Scripts/Activate.ps1
```

If you see an execution policy error:
```powershell
# Run PowerShell as Administrator once
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# Then re-run activation
./venv/Scripts/Activate.ps1
```

**4. Install Dependencies**
```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

**5. Initialize Database**
```powershell
$env:FLASK_APP = "app.py"
python seed_pricing.py
```

**6. Run Development Server**
```powershell
$env:FLASK_APP = "app.py"
flask run --debug
```

### macOS/Linux Setup

**1. Clone and Setup**
```bash
git clone <your-repo-url> smartprintpro
cd smartprintpro
python3 -m venv venv
source venv/bin/activate
```

**2. Install and Run**
```bash
pip install -U pip
pip install -r requirements.txt
python seed_pricing.py
export FLASK_APP=app.py
flask run --debug
```

### Git Workflow

**Create Feature Branch**
```bash
git checkout -b feature/my-feature
```

**Commit Changes**
```bash
git add .
git commit -m "Description of changes"
git push -u origin feature/my-feature
```

**Merge to Main**
```bash
git checkout main
git pull origin main
git merge feature/my-feature
git push origin main
# Optional: Delete feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

---

## Database Schema

### User Models

#### AbstractUser (Base Class)
```python
- id: Integer (Primary Key)
- full_name: String(120)
- email: String(120) Unique
- phone: String(30)
- organization: String(120) Optional
- password_hash: String(255)
- active: Boolean (default True)
- created_at: DateTime
- user_type: String (customer, vendor, admin)
```

#### Customer
```python
Inherits: AbstractUser
Table: customers
user_type: "customer"
```

#### Vendor
```python
Inherits: AbstractUser
Table: vendors
user_type: "vendor"
Additional Fields:
- business_name: String(200)
- business_address: String(300)
- business_type: String(100)
- services_offered: Text (comma-separated)
- tax_id: String(50)
```

#### Admin
```python
Inherits: AbstractUser
Table: admins
user_type: "admin"
```

### Order Management

#### Order
```python
- id: Integer (Primary Key)
- customer_id: ForeignKey(customers.id)
- vendor_id: ForeignKey(vendors.id) Optional
- order_number: String(50) Unique (e.g., ORD-20241205-0001)
- status: String(50) default "pending"
  States: pending, awaiting_vendor, quoted, quote_revised, 
          accepted, in_progress, ready, dispatched, completed
- base_fee: Float (default 75.0)
- subtotal: Float
- total_amount: Float
- paid_amount: Float
- payment_status: String(50) (unpaid, partial, paid)
- payment_date: DateTime
- customer_notes: Text
- vendor_notes: Text
- created_at: DateTime
- updated_at: DateTime
- vendor_assigned_at: DateTime
- accepted_at: DateTime
- completed_at: DateTime
- dispatched_at: DateTime
- received_at: DateTime

Relationships:
- customer → Customer
- vendor → Vendor
- order_items → List[OrderItem]
- quotes → List[Quote]
- status_history → List[OrderStatusHistory]
- review → Review (one-to-one)
```

#### OrderItem
```python
- id: Integer (Primary Key)
- order_id: ForeignKey(orders.id)
- service_category: String(100)
- service_type: String(200)
- quantity: Integer
- unit_price: Float
- total_price: Float
- file_name: String(255)
- file_path: String(500)
- file_type: String(50) (pdf, docx, image)
- file_size: Integer (bytes)
- image_width: Integer
- image_height: Integer
- image_format: String(20)
- page_count: Integer
- specifications: Text (JSON)
- created_at: DateTime
```

#### OrderStatusHistory
```python
- id: Integer (Primary Key)
- order_id: ForeignKey(orders.id)
- old_status: String(50)
- new_status: String(50)
- changed_by_id: Integer
- changed_by_type: String(20) (customer, vendor, admin)
- notes: Text
- created_at: DateTime

Property:
- changed_by_name: Returns user's full name
```

### Pricing & Quotes

#### ServicePrice
```python
- id: Integer (Primary Key)
- category: String(100)
- service_name: String(200)
- unit_price_min: Float
- unit_price_max: Float
- unit: String(50) (per page, per photo, etc.)
- description: Text
- active: Boolean
- created_at: DateTime
- updated_at: DateTime

Property:
- average_price: (min + max) / 2
```

#### Quote
```python
- id: Integer (Primary Key)
- order_id: ForeignKey(orders.id)
- quote_number: Integer (version for this order)
- base_fee: Float
- subtotal: Float
- total_amount: Float
- vendor_message: Text
- customer_response: Text
- status: String(50) (pending, accepted, rejected, revised)
- sent_by_vendor_at: DateTime
- responded_at: DateTime
- created_at: DateTime

Relationships:
- order → Order
- quote_items → List[QuoteItem]
```

#### QuoteItem
```python
- id: Integer (Primary Key)
- quote_id: ForeignKey(quotes.id)
- order_item_id: ForeignKey(order_items.id)
- unit_price: Float (vendor-adjusted)
- total_price: Float (vendor-adjusted)
- vendor_notes: Text (price justification)

Relationships:
- quote → Quote
- order_item → OrderItem
```

### Reviews

#### Review
```python
- id: Integer (Primary Key)
- order_id: ForeignKey(orders.id) Unique
- customer_id: ForeignKey(customers.id)
- vendor_id: ForeignKey(vendors.id)
- rating: Integer (1-5)
- comment: Text
- created_at: DateTime
- updated_at: DateTime

Relationships:
- order → Order
- customer → Customer
- vendor → Vendor
```

---

## Vendor-Customer Workflow Implementation

### ✅ Completed Components

#### 1. Database Models
All models created with proper relationships:
- Order with vendor assignment
- Quote and QuoteItem for negotiations
- OrderStatusHistory for audit trail
- Review for customer feedback

#### 2. Vendor Dashboard Template
`templates/vendor/vendordash.html` includes:
- 4 tabs (Available, My Orders, In Progress, Completed)
- Statistics cards
- Order cards with quick actions
- Review display
- Tab switching functionality

#### 3. Updated Imports
App.py imports all new models

#### 4. Database Seeding
Pricing data with 34 service entries

### 🚧 TODO: Routes Implementation

#### Vendor Routes (app.py)

```python
@app.route("/vendor/order/<int:order_id>")
@roles_required("vendor")
def vendor_view_order(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    return render_template("vendor/order_detail.html", order=order)

@app.route("/vendor/order/<int:order_id>/claim", methods=["POST"])
@roles_required("vendor")
def vendor_claim_order(order_id):
    """Claim an available order"""
    order = Order.query.get_or_404(order_id)
    
    # Check if order is still available
    if order.vendor_id is not None:
        flash("This order has already been claimed.", "error")
        return redirect(url_for("dashboard"))
    
    # Assign vendor
    order.vendor_id = current_user.id
    order.vendor_assigned_at = datetime.utcnow()
    order.add_status_change("awaiting_vendor", current_user.id, "vendor", 
                           f"{current_user.business_name} claimed this order")
    
    db.session.commit()
    flash("Order claimed successfully!", "success")
    return redirect(url_for("vendor_manage_order", order_id=order.id))

@app.route("/vendor/order/<int:order_id>/manage", methods=["GET", "POST"])
@roles_required("vendor")
def vendor_manage_order(order_id):
    """Create or revise quote"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure this vendor owns the order
    if order.vendor_id != current_user.id:
        flash("You don't have access to this order.", "error")
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        # Get next quote number
        quote_number = order.quote_count + 1
        
        # Create new quote
        quote = Quote(
            order_id=order.id,
            quote_number=quote_number,
            base_fee=float(request.form.get("base_fee", order.base_fee)),
            vendor_message=request.form.get("vendor_message", ""),
            status="pending"
        )
        
        # Create quote items with adjusted pricing
        subtotal = 0
        for item in order.order_items:
            adjusted_price = float(request.form.get(f"item_{item.id}_price", item.unit_price))
            adjusted_total = adjusted_price * item.quantity
            
            quote_item = QuoteItem(
                order_item_id=item.id,
                unit_price=adjusted_price,
                total_price=adjusted_total,
                vendor_notes=request.form.get(f"item_{item.id}_notes", "")
            )
            quote.quote_items.append(quote_item)
            subtotal += adjusted_total
        
        quote.subtotal = subtotal
        quote.total_amount = quote.base_fee + subtotal
        
        db.session.add(quote)
        
        # Update order
        order.base_fee = quote.base_fee
        order.subtotal = subtotal
        order.total_amount = quote.total_amount
        
        new_status = "quoted" if quote_number == 1 else "quote_revised"
        order.add_status_change(new_status, current_user.id, "vendor",
                               f"Quote #{quote_number} sent")
        
        db.session.commit()
        
        flash(f"Quote #{quote_number} sent to customer!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("vendor/manage_order.html", order=order)

@app.route("/vendor/order/<int:order_id>/status", methods=["POST"])
@roles_required("vendor")
def vendor_update_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    
    if order.vendor_id != current_user.id:
        flash("You don't have access to this order.", "error")
        return redirect(url_for("dashboard"))
    
    new_status = request.form.get("new_status")
    notes = request.form.get("notes", "")
    
    order.add_status_change(new_status, current_user.id, "vendor", notes)
    
    db.session.commit()
    
    flash(f"Order status updated to {new_status.replace('_', ' ').title()}", "success")
    return redirect(url_for("dashboard"))
```

#### Update Dashboard Route

```python
@app.route("/dashboard")
@login_required
def dashboard():
    template = {
        "customer": "user/userdash.html",
        "vendor": "vendor/vendordash.html",
        "admin": "admin/admindash.html",
    }.get(current_user.user_type)

    if not template:
        flash("Unknown user type.", "error")
        return redirect(url_for("login"))

    extra_context = {}
    
    if current_user.user_type == "admin":
        extra_context["user_counts"] = {
            "customers": Customer.query.count(),
            "vendors": Vendor.query.count(),
            "admins": Admin.query.count(),
        }
        extra_context["pending_reset_count"] = PasswordResetRequest.query.filter_by(status="pending").count()
        
    elif current_user.user_type == "customer":
        extra_context["orders"] = Order.query.filter_by(
            customer_id=current_user.id
        ).order_by(Order.created_at.desc()).all()
        
    elif current_user.user_type == "vendor":
        from sqlalchemy import func, extract
        
        # Get orders for each tab
        available_orders = Order.query.filter_by(
            vendor_id=None, status="pending"
        ).order_by(Order.created_at.desc()).all()
        
        assigned_orders = Order.query.filter_by(
            vendor_id=current_user.id
        ).filter(Order.status.in_(["awaiting_vendor", "quoted", "quote_revised"])).order_by(
            Order.vendor_assigned_at.desc()
        ).all()
        
        in_progress_orders = Order.query.filter_by(
            vendor_id=current_user.id
        ).filter(Order.status.in_(["accepted", "in_progress", "ready", "dispatched"])).order_by(
            Order.accepted_at.desc()
        ).all()
        
        completed_orders = Order.query.filter_by(
            vendor_id=current_user.id, status="completed"
        ).order_by(Order.completed_at.desc()).limit(20).all()
        
        # Calculate statistics
        current_month = datetime.now().month
        current_year = datetime.now().year
        completed_this_month = Order.query.filter_by(
            vendor_id=current_user.id, status="completed"
        ).filter(
            extract('month', Order.completed_at) == current_month,
            extract('year', Order.completed_at) == current_year
        ).count()
        
        # Calculate average rating
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
            vendor_id=current_user.id
        ).scalar()
        
        extra_context = {
            "available_orders": available_orders,
            "assigned_orders": assigned_orders,
            "in_progress_orders": in_progress_orders,
            "completed_orders": completed_orders,
            "stats": {
                "available": len(available_orders),
                "assigned": len(assigned_orders),
                "in_progress": len(in_progress_orders),
                "completed_this_month": completed_this_month,
                "average_rating": avg_rating or 0
            }
        }

    return render_template(template, user=current_user, **extra_context)
```

#### Customer Routes

```python
@app.route("/customer/order/<int:order_id>")
@roles_required("customer")
def customer_view_order(order_id):
    """View order details and tracking"""
    order = Order.query.get_or_404(order_id)
    
    if order.customer_id != current_user.id:
        flash("You don't have access to this order.", "error")
        return redirect(url_for("dashboard"))
    
    return render_template("user/order_detail.html", order=order)

@app.route("/customer/order/<int:order_id>/quote/<int:quote_id>/respond", methods=["POST"])
@roles_required("customer")
def customer_respond_to_quote(order_id, quote_id):
    """Accept or request revision of quote"""
    order = Order.query.get_or_404(order_id)
    quote = Quote.query.get_or_404(quote_id)
    
    if order.customer_id != current_user.id:
        flash("You don't have access to this order.", "error")
        return redirect(url_for("dashboard"))
    
    action = request.form.get("action")  # "accept" or "revise"
    customer_response = request.form.get("customer_response", "")
    
    if action == "accept":
        quote.status = "accepted"
        quote.responded_at = datetime.utcnow()
        quote.customer_response = customer_response
        
        order.add_status_change("accepted", current_user.id, "customer",
                               "Customer accepted quote")
        order.accepted_at = datetime.utcnow()
        
        flash("Quote accepted! Vendor will begin processing your order.", "success")
    else:
        quote.status = "revised"
        quote.responded_at = datetime.utcnow()
        quote.customer_response = customer_response
        
        order.add_status_change("quote_revised", current_user.id, "customer",
                               "Customer requested quote revision")
        
        flash("Revision request sent to vendor.", "success")
    
    db.session.commit()
    return redirect(url_for("customer_view_order", order_id=order.id))

@app.route("/customer/order/<int:order_id>/confirm-receipt", methods=["POST"])
@roles_required("customer")
def customer_confirm_receipt(order_id):
    """Confirm order received"""
    order = Order.query.get_or_404(order_id)
    
    if order.customer_id != current_user.id:
        flash("You don't have access to this order.", "error")
        return redirect(url_for("dashboard"))
    
    order.add_status_change("completed", current_user.id, "customer",
                           "Customer confirmed receipt")
    order.completed_at = datetime.utcnow()
    order.received_at = datetime.utcnow()
    
    db.session.commit()
    
    flash("Thank you for confirming! Please leave a review.", "success")
    return redirect(url_for("customer_view_order", order_id=order.id))

@app.route("/customer/order/<int:order_id>/review", methods=["POST"])
@roles_required("customer")
def customer_submit_review(order_id):
    """Submit review for completed order"""
    order = Order.query.get_or_404(order_id)
    
    if order.customer_id != current_user.id:
        flash("You don't have access to this order.", "error")
        return redirect(url_for("dashboard"))
    
    if order.status != "completed":
        flash("You can only review completed orders.", "error")
        return redirect(url_for("customer_view_order", order_id=order.id))
    
    # Check if review already exists
    if order.review:
        flash("You have already reviewed this order.", "error")
        return redirect(url_for("customer_view_order", order_id=order.id))
    
    rating = int(request.form.get("rating"))
    comment = request.form.get("comment", "")
    
    review = Review(
        order_id=order.id,
        customer_id=current_user.id,
        vendor_id=order.vendor_id,
        rating=rating,
        comment=comment
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash("Thank you for your review!", "success")
    return redirect(url_for("customer_view_order", order_id=order.id))
```

### TODO: Templates Needed

#### 1. `templates/vendor/manage_order.html`
Form to create/revise quotes with:
- Order details display
- Item pricing adjustment inputs
- Vendor message textarea
- Quote history display
- Submit button

#### 2. `templates/user/order_detail.html`
Customer order tracking page with:
- Order progress timeline
- Vendor information
- Order items list
- Quote history with accept/reject buttons
- Confirm receipt button (when dispatched)
- Review form (when completed)

### TODO: Forms (forms.py)

```python
class QuoteForm(FlaskForm):
    base_fee = FloatField("Base Fee", validators=[DataRequired()])
    vendor_message = TextAreaField("Message to Customer")
    submit = SubmitField("Send Quote")

class QuoteResponseForm(FlaskForm):
    action = SelectField("Action", 
                        choices=[("accept", "Accept Quote"), 
                                ("revise", "Request Revision")])
    customer_response = TextAreaField("Your Feedback")
    submit = SubmitField("Submit")

class ReviewForm(FlaskForm):
    rating = SelectField("Rating", 
                        choices=[(1, "1 Star"), (2, "2 Stars"), 
                                (3, "3 Stars"), (4, "4 Stars"), (5, "5 Stars")], 
                        coerce=int, validators=[DataRequired()])
    comment = TextAreaField("Review Comment", validators=[Optional()])
    submit = SubmitField("Submit Review")
```

---

## Testing Guide

### Manual Testing Workflow

#### 1. Create Test Accounts

**Admin** (pre-seeded):
- Email: admin@smartprintpro.com
- Password: Admin@123

**Vendor Accounts** (create via signup):
- Business Name: "Quick Print Shop"
- Services: Select multiple checkboxes
- Email: vendor1@test.com
- Password: Test@123

**Customer Accounts** (create via signup):
- Full Name: "John Customer"
- Email: customer1@test.com
- Password: Test@123

#### 2. Test Order Creation

1. Login as customer
2. Navigate to "Create Order"
3. Add multiple items with different services
4. Upload test files (PDF, images)
5. Add customer notes
6. Submit order
7. Verify order appears in customer dashboard

#### 3. Test Vendor Workflow

1. Login as vendor
2. View "Available Orders" tab
3. Click "Claim Order" on a pending order
4. Verify order moves to "My Orders" tab
5. Click "Send Quote"
6. Adjust prices for items
7. Add vendor message
8. Submit quote
9. Verify quote sent successfully

#### 4. Test Quote Negotiation

1. Login as customer
2. View order detail
3. See vendor's quote
4. Request revision with feedback
5. Login as vendor
6. View customer feedback
7. Send revised quote
8. Customer accepts revised quote

#### 5. Test Order Processing

1. Vendor updates status to "in_progress"
2. Vendor marks as "ready"
3. Vendor marks as "dispatched"
4. Customer confirms receipt
5. Customer leaves review (rating + comment)

#### 6. Test Edge Cases

- Multiple vendors trying to claim same order
- Customer accepting old quote when new one exists
- Vendor accessing order they don't own
- Customer accessing another customer's order
- Review submission for incomplete orders

### Automated Testing

Create test file `test_workflow.py`:

```python
import unittest
from app import create_app
from extension import db
from models import Customer, Vendor, Order, Quote, Review

class WorkflowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_order_creation(self):
        # Test order creation workflow
        pass
    
    def test_vendor_claim(self):
        # Test vendor claiming order
        pass
    
    def test_quote_negotiation(self):
        # Test quote send and revision
        pass
```

---

## API Routes

### Public Routes
- `GET /` - Homepage
- `GET /vendors` - Vendors listing
- `GET /features` - Features page
- `GET /how-it-works` - How it works page
- `GET /signup` - Registration form
- `POST /signup` - Process registration
- `GET /login` - Login form
- `POST /login` - Process login
- `GET /forgot-password` - Password reset request
- `POST /forgot-password` - Process reset request

### Authenticated Routes
- `GET /dashboard` - Role-based dashboard redirect
- `GET /logout` - Logout user
- `GET /account/edit` - Edit account (customer/vendor)
- `POST /account/edit` - Update account

### Customer Routes
- `GET /create-order` - Order creation form
- `POST /create-order` - Submit order
- `GET /customer/order/<id>` - View order details
- `POST /customer/order/<id>/quote/<quote_id>/respond` - Respond to quote
- `POST /customer/order/<id>/confirm-receipt` - Confirm delivery
- `POST /customer/order/<id>/review` - Submit review

### Vendor Routes
- `GET /vendor/order/<id>` - View order details
- `POST /vendor/order/<id>/claim` - Claim order
- `GET /vendor/order/<id>/manage` - Quote management page
- `POST /vendor/order/<id>/manage` - Submit quote
- `POST /vendor/order/<id>/status` - Update status

### Admin Routes
- `GET /admin/overview` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/users/<type>/<id>/edit` - Edit user
- `POST /admin/users/<type>/<id>/edit` - Update user
- `GET /admin/password-requests` - Password reset requests
- `GET /admin/password-requests/<id>` - Reset request detail
- `POST /admin/password-requests/<id>` - Process reset

---

## Forms Reference

### RegistrationForm
- `user_type`: Customer or Vendor selection
- `full_name`: Customer's full name
- `business_name`: Vendor's business name (conditional)
- `business_address`: Vendor address (conditional)
- `business_type`: Print shop type (conditional)
- `services_offered`: Multi-checkbox for vendor services (conditional)
- `email`: Email address (unique)
- `phone`: Phone number
- `password`: Password with strength requirements
- `confirm_password`: Password confirmation

### LoginForm
- `email`: Email address
- `password`: Password
- `remember`: Remember me checkbox

### AccountUpdateForm
- `full_name`: Update name
- `phone`: Update phone
- `organization`: Optional organization
- `new_password`: Optional password change
- `confirm_new_password`: Password confirmation

### AdminUserEditForm
- `full_name`: Edit user name
- `phone`: Edit phone
- `organization`: Edit organization
- `active`: Activate/deactivate account

### AdminPasswordResetForm
- `new_password`: New password
- `confirm_password`: Confirmation
- `admin_note`: Optional admin note

---

## Troubleshooting

### Common Issues

**"Circular dependency detected" during migration**
- Solution: Recreate database from scratch
```bash
rm -f instance/app.db
python -c "from app import app; from extension import db; app.app_context().push(); db.create_all()"
python seed_pricing.py
```

**"Multiple heads are present" migration error**
```bash
flask db merge -m "merge_heads" heads
flask db upgrade
```

**Form not displaying checkboxes**
- Check `forms.py` has `MultiCheckboxField` class
- Verify `services_offered` field uses `MultiCheckboxField`
- Ensure template checks `if form.services_offered.data` before iterating

**"NoneType is not iterable" in templates**
- Add null checks: `{% if data %}...{% endif %}`
- Initialize empty lists/dicts in routes

**File upload fails**
- Check `uploads/` directory exists
- Verify file size under 50MB
- Ensure file extension is allowed

**Database locked**
- Close DB Browser or any SQLite viewer
- Check no other Flask instance is running

### Development Tips

**View SQL Queries**
```python
app.config['SQLALCHEMY_ECHO'] = True
```

**Debug Toolbar**
```bash
pip install flask-debugtoolbar
```

**Shell Access**
```bash
flask shell
>>> from models import *
>>> Order.query.all()
```

**Clear Database**
```bash
rm -f instance/app.db
```

### Performance Optimization

**Database Indexing**
Add indexes to frequently queried fields:
```python
- order_number
- email
- vendor_id
- customer_id
- status
```

**Query Optimization**
- Use `.filter()` instead of Python filtering
- Add `.limit()` to large result sets
- Use `lazy='dynamic'` for large relationships
- Enable query caching for static data

**File Storage**
- Move uploads to cloud storage (S3, etc.)
- Implement CDN for static assets
- Add file compression

---

## Next Steps

1. ✅ **Complete**: Database models and vendor dashboard
2. **TODO**: Implement all vendor routes in app.py
3. **TODO**: Update dashboard route with vendor statistics
4. **TODO**: Create `vendor/manage_order.html` template
5. **TODO**: Implement all customer routes
6. **TODO**: Create `user/order_detail.html` template
7. **TODO**: Add forms to forms.py
8. **TODO**: Test complete workflow
9. **TODO**: Add email notifications
10. **TODO**: Implement payment processing

Refer to `IMPLEMENTATION_STATUS.md` for detailed code samples and implementation guidance.
