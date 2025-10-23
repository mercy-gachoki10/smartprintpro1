# SmartPrint Pro - Pages & Structure Guide

## Overview

SmartPrint Pro is organized with a **template inheritance system** using a base template that all pages extend. This ensures a consistent design and reusable header/footer/navigation across the entire site.

## Template Architecture

### `base.html` - Master Template
The foundational template that contains:
- **Header** with logo and navigation (all pages share this)
- **Footer** (all pages share this)
- **Contact modal** (shared across all pages)
- **Shared scripts** for modal and scroll functions
- **Block placeholders** for page-specific content

All other templates extend this using Jinja2 template inheritance:
```html
{% extends "base.html" %}
{% block content %}
  <!-- Page-specific content -->
{% endblock %}
```

## Pages & Routes

### 1. **Home Page** - `/` - `index.html`
**File:** `templates/index.html`

**What it shows:**
- Hero section with main call-to-action
- Search box with quick category filters
- Featured vendors showcase (demo: BoldPrint, GraphicDesign Nairobi, SPU Print)
- How it works section (3 simple steps)
- Key features showcase

**Features:**
- Live search filtering by tags
- Vendor cards with ratings and buttons
- Quick category shortcuts (uniforms, t-shirts, banners, etc.)
- Contact modal for reaching out to vendors

---

### 2. **Vendors Page** - `/vendors` - `vendors.html`
**File:** `templates/vendors.html`

**What it shows:**
- Complete list of print vendors across Kenya
- Organized by location (Nairobi, Mombasa, Kisumu)
- 8+ demo vendors with varied services and specialties

**Vendors Featured:**
- **Nairobi:** GraphicDesign Nairobi, BoldPrint, SPU Print, CustomThreads Kenya
- **Mombasa:** Coastal Prints, Elite Printing Services, PrintPack Solutions
- **Kisumu:** Kisumu Print Hub

**Features:**
- Location-based filtering (Nairobi, Mombasa, Kisumu, Premium, Fast Delivery)
- Search by vendor name or service
- Vendor profiles with location emoji, services, ratings, order count
- Statistics section showing coverage (50+ vendors, 15+ cities, 5000+ orders)
- Color-coded vendor logos for easy identification

---

### 3. **Features Page** - `/features` - `features.html`
**File:** `templates/features.html`

**What it shows:**
- 8 feature categories with detailed explanations
- All capabilities of the SmartPrint Pro platform

**Feature Sections:**
1. **🔍 Smart Search & Discovery** - Location, services, ratings, quick filters
2. **📤 Smart Upload & Instant Quotes** - AI file check, price breakdown, format support
3. **💳 Secure Payments & M-Pesa** - Local payment integration, multiple options
4. **📦 Real-Time Order Tracking** - Live status, production timeline, delivery tracking
5. **🏢 Complete Vendor Profiles** - Services, portfolio, reviews, availability
6. **⚖️ Smart Comparison Tools** - Side-by-side quotes, multiple vendors, quality metrics
7. **👥 User Dashboard & Account** - Order history, saved designs, bulk ordering
8. **💼 Business & Enterprise Tools** - Team accounts, budgets, API access, white-label

**Features:**
- Feature cards organized by category
- Call-to-action buttons (Browse Vendors, Get Started)

---

### 4. **How It Works Page** - `/how-it-works` - `how_it_works.html`
**File:** `templates/how_it_works.html`

**What it shows:**
- Step-by-step explanation of the SmartPrint Pro process
- FAQ section with expandable answers
- Platform benefits and differentiators

**3-Step Process:**
1. **🔍 Search & Find** - Browse vendors, check ratings, view portfolios
2. **📤 Upload & Quote** - Upload files, AI check, instant pricing
3. **💳 Pay & Track** - Choose vendor, pay securely, track in real-time

**Additional Sections:**
- **What Makes SmartPrint Pro Different** - Speed, Transparency, Local focus, Security, Ease, Quality
- **8 FAQs** with expandable answers (clicking expands/collapses)
  - Quote timing
  - File formats accepted
  - M-Pesa security
  - Order tracking
  - Satisfaction guarantee
  - Rush orders
  - Minimum quantities
  - Delivery areas

**Features:**
- Interactive FAQ with toggle functionality
- Pro tips in highlighted boxes
- Responsive numbered steps with icons
- CTA buttons for browsing vendors

---

### 5. **Login Page** - `/login` - `login.html`
**File:** `templates/login.html`

**What it shows:**
- Login and Sign Up forms in tabbed interface
- Authentication and account creation flows (demo)

**Login Tab:**
- Email/phone input
- Password input
- Forgot password link
- Social login options (Google, Phone)
- Link to switch to Sign Up

**Sign Up Tab:**
- Full name input
- Email input
- Phone number input
- Account type dropdown (Individual, Business, Vendor)
- Password and confirm password inputs
- Terms & Privacy Policy checkbox
- Link to switch to Login

**Features:**
- Clean, modern form design with focus states
- Tab switching between Login/Sign Up
- Social login buttons (demo)
- Account type selection for different user roles
- Success messages (demo alerts)
- Info section highlighting benefits

**Custom Styles:**
- Purple theme matching the brand
- Form validation states
- Responsive card layout
- Beautiful form groups and buttons

---

## Navigation Structure

**Header Navigation (on all pages):**
```
SmartPrint Pro Logo → Home | Vendors | How it Works | Features | Login
```

Each link directs to:
- Home → `/`
- Vendors → `/vendors`
- How it Works → `/how-it-works`
- Features → `/features`
- Login → `/login`

---

## File Organization

```
smartprintpro1/
├── app.py                          # Flask app with all routes
├── templates/
│   ├── base.html                   # Master template (header, footer, modal)
│   ├── index.html                  # Home page
│   ├── vendors.html                # Vendors directory
│   ├── features.html               # Features showcase
│   ├── how_it_works.html          # How it works guide
│   └── login.html                  # Login/Sign Up
├── static/
│   ├── css/
│   │   └── main.css                # Unified styles for all pages
│   └── assets/
│       └── images/
│           └── logo.png            # Brand logo (optional)
├── venv/                           # Virtual environment
└── README.md                        # Project documentation
```

---

## Color Scheme & Branding

**CSS Variables (in `main.css`):**
```css
--purple: #6B21A8       /* Primary brand color */
--gold: #D4AF37         /* Accent/highlight color */
--white: #ffffff        /* Light backgrounds */
--black: #000000        /* Text color */
--muted: #6b6b77        /* Secondary text */
--bg: #faf8ff           /* Page background */
```

---

## Key Features of Base Template

### Shared Elements
1. **Header** - Brand logo (PNG fallback to SVG), navigation links
2. **Footer** - Copyright notice, customized for Kenya focus
3. **Modal** - Reusable contact form for vendors
4. **Shared Scripts** - Modal functions, scroll helpers

### Block Areas
- `{% block title %}` - Page-specific title tags
- `{% block content %}` - Main page content
- `{% block extra_css %}` - Page-specific styles
- `{% block extra_js %}` - Page-specific JavaScript

---

## Demo Features

All forms and buttons are **demo functionality** showing:
- Form submission alerts
- Modal interactions
- Tab switching
- Search/filter functionality

To implement real functionality:
- Connect forms to backend routes
- Add database models
- Implement user authentication
- Add payment processing (M-Pesa)
- Implement file upload handling

---

## Responsive Design

**Breakpoints:**
- **Desktop:** > 768px - Full layout with multi-column grids
- **Tablet:** 600px - 768px - Adjusted spacing, 2-column grids
- **Mobile:** < 600px - Single column, optimized touch targets

**Mobile Optimizations:**
- Single column layouts
- Larger touch targets for buttons
- Simplified navigation
- Full-width inputs
- Responsive fonts

---

## How to Add a New Page

1. **Create template file** in `templates/` directory:
   ```html
   {% extends "base.html" %}
   {% block title %}Page Title{% endblock %}
   {% block content %}
     <!-- Your content here -->
   {% endblock %}
   ```

2. **Add Flask route** in `app.py`:
   ```python
   @app.route("/page-name")
   def page_name():
       return render_template("page_name.html")
   ```

3. **Update navigation** in `base.html` if needed:
   ```html
   <a href="/page-name">Page Name</a>
   ```

---

## Testing the App

**Start the development server:**
```bash
# Activate virtual environment
./venv/Scripts/Activate.ps1

# Run Flask
$env:FLASK_APP = "app.py"
flask run --debug
```

**Visit:** `http://127.0.0.1:5000`

**Test all pages:**
- / (Home)
- /vendors (Vendors)
- /features (Features)
- /how-it-works (How it Works)
- /login (Login)

---

## Next Steps

To enhance this further:
1. **Database Integration** - Store vendors, users, orders
2. **Authentication** - Real login/signup with sessions
3. **File Upload** - Design file upload handling
4. **Payment Integration** - M-Pesa and card payments
5. **Order Management** - Create and track orders
6. **Vendor Dashboard** - Backend for vendors
7. **Admin Panel** - Manage vendors, users, orders
8. **Email Notifications** - Order updates via email/SMS

---

## Support & Customization

Each page is fully customizable. Modify:
- **Colors:** Update CSS variables in `main.css`
- **Content:** Edit HTML in template files
- **Functionality:** Add JavaScript in `{% block extra_js %}`
- **Styles:** Add CSS in `{% block extra_css %}`

All pages inherit the base design but can override it with custom blocks.
