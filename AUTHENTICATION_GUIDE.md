# SmartPrint Pro - Authentication Guide

## Overview

The authentication system has been redesigned with separated login and signup pages, and a user type selector to accommodate three account types: **Customer**, **Employee**, and **Administrator**.

---

## 📄 New Page Structure

### **Login Page** (`/login`)
**File:** `templates/login.html`

Dedicated page for existing users to sign in.

**Features:**
- User type selector (Customer, Employee, Administrator)
- Dynamic login message based on selected user type
- Email/Phone and password inputs
- "Forgot password?" link
- Social login options (Google, Phone)
- Link to signup page
- User type information box

**User Types & Their Messages:**
1. **Customer** 👤
   - Message: "Login to your SmartPrint Pro customer account"
   - Info: Browse vendors, upload designs, get quotes, and track orders

2. **Employee** 👨‍💼
   - Message: "Login to your SmartPrint Pro employee dashboard"
   - Info: Manage customer orders, process quotes, and track shipments

3. **Administrator** ⚙️
   - Message: "Login to SmartPrint Pro administration panel"
   - Info: Manage vendors, users, orders, and system settings

**URL:** `/login`  
**Route in app.py:** `@app.route("/login")`

---

### **Sign Up Page** (`/signup`)
**File:** `templates/signup.html`

Dedicated page for new users to create an account.

**Features:**
- Account type selector (Customer, Employee, Administrator)
- Registration form with fields:
  - Full Name
  - Email Address
  - Phone Number
  - Organization/Company Name (optional for customers, required for admin)
  - Password
  - Confirm Password
  - Terms & Privacy agreement checkbox
- Dynamic account type descriptions
- Password validation (minimum 8 characters)
- Password matching validation
- Link to login page
- Account type description box

**Account Type Behaviors:**
1. **Customer** 👤
   - Organization field: Optional
   - Description: Browse vendors, upload designs, get quotes, track orders

2. **Employee** 👨‍💼
   - Organization field: Optional
   - Description: Process customer orders, manage quotes, handle shipments

3. **Administrator** ⚙️
   - Organization field: Required (shows "Admin code required")
   - Description: Manage vendors, users, orders, system settings

**URL:** `/signup`  
**Route in app.py:** `@app.route("/signup")`

---

## 🔐 User Type Selector

Both pages feature a user type selector with three buttons:

### Desktop Layout
```
[👤 Customer] [👨‍💼 Employee] [⚙️ Administrator]
```

### Mobile Layout
```
[👤 Customer]
[👨‍💼 Employee]
[⚙️ Administrator]
```

### Features
- **Active State:** Purple background with white text
- **Hover State:** Purple border with purple text
- **Responsive:** Stacks vertically on mobile
- **Dynamic Content:** Page content updates based on selection

---

## 🔄 Navigation Between Pages

**From Login to Signup:**
```
Click "Create one here" link → Goes to /signup
```

**From Signup to Login:**
```
Click "Login here" link → Goes to /login
```

**From Navigation:**
```
Header "Login" link → Always goes to /login
(Add "Signup" link to header if needed)
```

---

## 📋 Form Validation

### Login Page
- ✅ Email/Phone: Required
- ✅ Password: Required

### Signup Page
- ✅ Full Name: Required
- ✅ Email: Required, must be valid email
- ✅ Phone: Required
- ✅ Organization: Optional (required for Admin type)
- ✅ Password: Required, minimum 8 characters
- ✅ Confirm Password: Must match password
- ✅ Terms Agreement: Required checkbox

---

## 🎨 Styling & Responsiveness

### Desktop (> 600px)
- 3-column user type selector
- Side-by-side form fields
- Full-width at max-width: 450px (login), 500px (signup)

### Mobile (≤ 600px)
- Single-column user type selector
- Stacked form fields
- Full-width forms
- 30px top margin
- 20px padding

### Touch-Friendly
- All buttons: minimum 44px height
- All inputs: 16px font size (prevents zoom on iOS)
- Adequate spacing between interactive elements

---

## 🔄 User Flow

```
Visitor arrives at SmartPrint Pro
    ↓
Click "Login" in header
    ↓
Lands on /login page
    ↓
Select account type (Customer/Employee/Admin)
    ↓
Page content updates dynamically
    ↓
Enter email/phone and password
    ↓
Click Login button
    ↓
(In real app: authenticate with backend)
    ↓
Redirect to dashboard based on user type
```

**Alternative Flow (New User):**
```
Visitor arrives at SmartPrint Pro
    ↓
Click "Create one here" link
    ↓
Lands on /signup page
    ↓
Select account type
    ↓
Fill in registration form
    ↓
Click "Create Account"
    ↓
(In real app: validate & create account)
    ↓
Redirect to login or auto-login
```

---

## 🛠️ Backend Integration

### Login Implementation
When integrating with backend:

```python
@app.route("/login", methods=["POST"])
def login():
    user_type = request.form.get('user_type')  # customer, employee, admin
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Validate credentials
    # Check user_type matches account
    # Redirect to appropriate dashboard
    
    return redirect(f"/dashboard/{user_type}")
```

### Signup Implementation
```python
@app.route("/signup", methods=["POST"])
def signup():
    user_type = request.form.get('account_type')
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    # Validate input
    # Create user in database
    # Send verification email
    
    return redirect("/login?registered=true")
```

### Database Fields
```
users table:
- id
- fullname
- email
- phone
- user_type (customer/employee/admin)
- password_hash (bcrypt hashed)
- organization (nullable)
- created_at
- updated_at
```

**Database Setup:**
The application uses Flask-SQLAlchemy with SQLite (default) or PostgreSQL support. To set up the database:

```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Create users table"

# Apply migration
flask db upgrade
```

Example model:
```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 🚀 Demo URLs

**Login:** `http://localhost:5000/login`  
**Signup:** `http://localhost:5000/signup`

### Testing Steps
1. Visit login page
2. Select different user types - notice message changes
3. Try to login (demo shows alert)
4. Click "Create one here"
5. Visit signup page
6. Select different account types - form updates
7. Try to signup (demo validates and shows alert)

---

## 📱 Mobile Testing

**Test on Different Devices:**
- iPhone (375px)
- iPad (768px)
- Android Phone (360px)
- Desktop (1920px)

**Key Checks:**
- ✅ User type buttons stack vertically
- ✅ Form fields are readable
- ✅ Buttons are touch-friendly (44px+)
- ✅ No horizontal scrolling
- ✅ Text is legible without zoom

---

## 🔒 Security Considerations

For production implementation:

1. **Password Security**
   - Hash passwords with bcrypt (included in requirements.txt)
   - Enforce minimum 8 characters (current)
   - Consider adding strength indicator
   - Example implementation:
     ```python
     from bcrypt import hashpw, gensalt, checkpw
     
     # Hash password
     password_hash = hashpw(password.encode('utf-8'), gensalt())
     
     # Verify password
     is_valid = checkpw(password.encode('utf-8'), stored_hash)
     ```

2. **CSRF Protection**
   - Add CSRF tokens to forms
   - Use Flask-WTF for form security (included in requirements.txt)
   - Example:
     ```python
     from flask_wtf import FlaskForm, CSRFProtect
     
     csrf = CSRFProtect(app)
     
     class LoginForm(FlaskForm):
         email = StringField('Email', validators=[DataRequired(), Email()])
         password = PasswordField('Password', validators=[DataRequired()])
     ```

3. **Rate Limiting**
   - Limit login attempts (5 per minute)
   - Implement CAPTCHA after failed attempts

4. **Email Verification**
   - Send verification link on signup
   - Don't allow login until verified

5. **Session Management**
   - Secure session cookies (HttpOnly, Secure flags)
   - Implement session timeout
   - Use Flask-Login for sessions (included in requirements.txt)
   - Example setup:
     ```python
     from flask_login import LoginManager, login_user, logout_user
     
     login_manager = LoginManager()
     login_manager.init_app(app)
     login_manager.login_view = 'login'
     ```

6. **Admin Account Creation**
   - Require invitation code
   - Only admins can create admin accounts
   - Log all admin account creations

---

## 📞 Support

For questions or issues with the authentication system, refer to:
- DEV_GUIDE_WINDOWS.md - Development setup
- PAGES_STRUCTURE.md - Overall site structure
- IMPLEMENTATION_SUMMARY.md - Technical details

---

**Last Updated:** October 23, 2025  
**Status:** ✅ Implementation Complete
