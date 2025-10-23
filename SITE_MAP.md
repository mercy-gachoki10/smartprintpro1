# SmartPrint Pro - Site Map & Information Architecture

## 🗺️ Site Navigation Map

```
                        SmartPrint Pro
                              |
                    ┌─────────┼─────────┐
                    |         |         |
                    v         v         v
                  Home     Vendors    Features
                    |         |         |
                    |         |         |
              ┌─────┴─────┬───┴───┬─────┴─────┐
              |           |       |           |
              v           v       v           v
          How It Works  Login   Search    Contact
                        |       By Tag     Modal
                        |
                    ┌───┴──────┐
                    |          |
                    v          v
                  Login      Sign Up
```

## 📄 Page Hierarchy

```
BASE TEMPLATE (base.html)
├── Header
│   ├── Logo + Brand Name
│   └── Navigation Links
│       ├── Home (/)
│       ├── Vendors (/vendors)
│       ├── How it Works (/how-it-works)
│       ├── Features (/features)
│       └── Login (/login)
├── Main Content ({% block content %})
├── Contact Modal (shared)
└── Footer
    └── Copyright
```

## 🏠 HOME PAGE (/)

```
index.html extends base.html

┌─────────────────────────────────────┐
│         HEADER + NAV                │
├─────────────────────────────────────┤
│           HERO SECTION              │
│  "Find trusted local print shops"   │
│  [Search Box] [Search Btn]          │
│  [Quick Filters: Uniform|Banner|...] │
├─────────────────────────────────────┤
│      FEATURED VENDORS (3 cols)      │
│  ┌─────────┬─────────┬─────────┐   │
│  │ Vendor1 │ Vendor2 │ Vendor3 │   │
│  └─────────┴─────────┴─────────┘   │
├─────────────────────────────────────┤
│    HOW IT WORKS (3 steps)           │
│  ┌─────────┬─────────┬─────────┐   │
│  │ Search  │  Upload │  Pay &  │   │
│  │ & Find  │ & Quote │ Track   │   │
│  └─────────┴─────────┴─────────┘   │
├─────────────────────────────────────┤
│    KEY FEATURES (4 features)        │
│  ┌─────────┬─────────┬─────────┬──┐│
│  │Feature 1│Feature 2│Feature 3│F4││
│  └─────────┴─────────┴─────────┴──┘│
├─────────────────────────────────────┤
│         FOOTER                      │
└─────────────────────────────────────┘
```

## 🏪 VENDORS PAGE (/vendors)

```
vendors.html extends base.html

┌─────────────────────────────────────┐
│         HEADER + NAV                │
├─────────────────────────────────────┤
│           HERO SECTION              │
│ "Print Vendors Across Kenya"        │
│ [Search Box] [Search Btn]           │
│ [Location Filters + Service Filters]│
├─────────────────────────────────────┤
│    VENDORS DIRECTORY (Multi-cols)   │
│  Nairobi Vendors:                   │
│  ├── GraphicDesign Nairobi          │
│  ├── BoldPrint (Premium)            │
│  ├── SPU Print                       │
│  └── CustomThreads Kenya            │
│                                      │
│  Mombasa Vendors:                    │
│  ├── Coastal Prints                  │
│  ├── Elite Printing Services         │
│  └── PrintPack Solutions            │
│                                      │
│  Kisumu Vendors:                     │
│  └── Kisumu Print Hub                │
├─────────────────────────────────────┤
│    STATISTICS SECTION               │
│  50+ Vendors | 15+ Cities | 5000+   │
│  Orders | 24-48hr Turnaround        │
├─────────────────────────────────────┤
│         FOOTER                      │
└─────────────────────────────────────┘
```

## ✨ FEATURES PAGE (/features)

```
features.html extends base.html

┌─────────────────────────────────────┐
│         HEADER + NAV                │
├─────────────────────────────────────┤
│           HERO SECTION              │
│ "Powerful Features for Smart Print" │
├─────────────────────────────────────┤
│   8 FEATURE CATEGORIES (cards)      │
│                                      │
│  1. 🔍 Search & Discovery           │
│  2. 📤 Upload & Quotes              │
│  3. 💳 Payments & M-Pesa            │
│  4. 📦 Order Tracking               │
│  5. 🏢 Vendor Profiles              │
│  6. ⚖️  Comparison Tools             │
│  7. 👥 User Dashboard               │
│  8. 💼 Business Tools               │
│                                      │
│  Each with 4 sub-features           │
├─────────────────────────────────────┤
│   CTA BUTTONS                       │
│  [Browse Vendors] [Get Started]     │
├─────────────────────────────────────┤
│         FOOTER                      │
└─────────────────────────────────────┘
```

## ❓ HOW IT WORKS PAGE (/how-it-works)

```
how_it_works.html extends base.html

┌─────────────────────────────────────┐
│         HEADER + NAV                │
├─────────────────────────────────────┤
│           HERO SECTION              │
│   "How SmartPrint Pro Works"        │
├─────────────────────────────────────┤
│    3-STEP PROCESS (detailed)        │
│                                      │
│  ① Search & Find                    │
│  └─ Browse, Filter, Check Ratings   │
│                                      │
│  ② Upload & Quote                   │
│  └─ Upload Files, Get Instant Quotes│
│                                      │
│  ③ Pay & Track                      │
│  └─ Secure Payment, Track Progress  │
├─────────────────────────────────────┤
│  DIFFERENTIATORS (6 features)       │
│  Speed | Transparency | Local       │
│  Security | Ease | Quality          │
├─────────────────────────────────────┤
│    FAQ SECTION (8 expandable)       │
│                                      │
│  ❓ How long for quote?             │
│  ❓ File formats?                   │
│  ❓ M-Pesa secure?                  │
│  ❓ Real-time tracking?             │
│  ❓ Not happy?                      │
│  ❓ Rush orders?                    │
│  ❓ Minimums?                       │
│  ❓ Delivery areas?                 │
├─────────────────────────────────────┤
│   CTA BUTTONS                       │
│  [Browse Vendors] [Back to Home]    │
├─────────────────────────────────────┤
│         FOOTER                      │
└─────────────────────────────────────┘
```

## 🔐 LOGIN PAGE (/login)

```
login.html extends base.html

┌─────────────────────────────────────┐
│         HEADER + NAV                │
├─────────────────────────────────────┤
│                                      │
│      LOGIN CARD (centered)          │
│  ┌───────────────────────────────┐  │
│  │ [Login Tab] [Sign Up Tab]     │  │
│  ├───────────────────────────────┤  │
│  │ LOGIN FORM:                   │  │
│  │ • Email/Phone input           │  │
│  │ • Password input              │  │
│  │ [Forgot Password?]            │  │
│  │ [LOGIN BUTTON]                │  │
│  │ ─── Or continue with ───      │  │
│  │ [Google] [Phone]              │  │
│  │ Need account? Sign up         │  │
│  └───────────────────────────────┘  │
│                                      │
│  ┌───────────────────────────────┐  │
│  │ SIGN UP FORM (hidden):        │  │
│  │ • Full Name                   │  │
│  │ • Email                       │  │
│  │ • Phone                       │  │
│  │ • Account Type (dropdown)     │  │
│  │ • Password                    │  │
│  │ • Confirm Password            │  │
│  │ • Terms & Privacy (checkbox)  │  │
│  │ [CREATE ACCOUNT BUTTON]       │  │
│  │ Have account? Login           │  │
│  └───────────────────────────────┘  │
│                                      │
│     WHY SMARTPRINT PRO? (4 items)   │
│  🔍 Find Vendors | 💰 Get Quotes    │
│  📦 Track Orders | 💳 Pay Safely    │
│                                      │
├─────────────────────────────────────┤
│         FOOTER                      │
└─────────────────────────────────────┘
```

## 🔄 Data Flow

```
User Journey:
├─ Lands on Home (/)
├─ Browses Vendors (/vendors)
│  └─ Filters by Location (Nairobi/Mombasa/Kisumu)
│  └─ Searches by Service
├─ Views Features (/features)
├─ Reads How It Works (/how-it-works)
├─ Creates Account (/login - Sign Up)
│  └─ Selects Account Type
│  └─ Sets Password
└─ Logs In (/login - Login)
   └─ Searches for Vendor
   └─ Uploads Design
   └─ Gets Quote
   └─ Pays via M-Pesa
   └─ Tracks Order
```

## 📱 Responsive Breakpoints

```
Desktop (> 768px)
├─ Multi-column layouts
├─ Side-by-side content
├─ Full header with links
└─ Grid layouts (2-4 columns)

Tablet (600px - 768px)
├─ 2-column layouts
├─ Stacked components
├─ Adjusted spacing
└─ 1-2 column grids

Mobile (< 600px)
├─ Single column layouts
├─ Full-width inputs
├─ Centered forms
├─ 1-column grids
├─ Simplified navigation
└─ Touch-friendly buttons
```

## 🔗 Internal Links Summary

```
FROM HOME (/):
├─ To Vendors (/vendors) - Featured vendor cards
├─ To Features (/features) - "Key features" section
├─ To How It Works (/how-it-works) - "How it works" section
└─ To Login (/login) - Navigation link

FROM VENDORS (/vendors):
├─ To Home (/) - Logo + nav link
├─ To Features (/features) - Nav link
├─ To How It Works (/how-it-works) - Nav link
└─ To Login (/login) - Nav link + Contact modal

FROM FEATURES (/features):
├─ To Vendors (/vendors) - "Browse Vendors" button
├─ To Home (/) - Logo + nav link
├─ To How It Works (/how-it-works) - Nav link
└─ To Login (/login) - "Get Started" button

FROM HOW IT WORKS (/how-it-works):
├─ To Vendors (/vendors) - "Browse Vendors" button
├─ To Home (/) - "Back to Home" button
└─ To Login (/login) - Nav link

FROM LOGIN (/login):
├─ To Home (/) - Logo + nav link
├─ Between Login/Sign Up - Tab buttons
└─ To Vendors (/vendors) - Nav link
```

## 🎨 Shared Components

```
HEADER (on all pages)
├─ Logo Image (PNG) / SVG Fallback
├─ Brand Name + Tagline
└─ Navigation Links (5)

FOOTER (on all pages)
├─ Copyright text
└─ Kenya focus attribution

MODAL (on all pages)
├─ Contact Form
├─ Vendor messaging
└─ Close button

SEARCH FUNCTIONALITY
├─ Text input
├─ Quick filters (buttons)
└─ Real-time filtering

VENDOR CARDS
├─ Logo (small)
├─ Name + location
├─ Services/tags
├─ Rating + order count
└─ Action buttons (View/Contact)
```

---

## 📊 Content Statistics

| Element | Count |
|---------|-------|
| Total Pages | 5 |
| Template Files | 6 (1 base + 5 pages) |
| Routes | 5 |
| Demo Vendors | 8+ |
| Feature Categories | 8 |
| FAQ Items | 8 |
| Responsive Breakpoints | 3 |
| Color Variables | 6 |
| Shared Components | 4 |

---

**Last Updated:** October 23, 2025  
**Status:** ✅ Complete Architecture
