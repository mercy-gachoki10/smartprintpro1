# SmartPrint Pro

## Overview
SmartPrint Pro is a comprehensive print shop management platform that connects customers with local print vendors. It features a complete vendor-customer workflow with price negotiations, order tracking, payments, and a review system.

## Key Features

### For Customers
- Create print orders with multiple items and file uploads
- Receive and review quotes from vendors
- Accept or request quote revisions
- Track order progress in real-time
- Confirm delivery and make payments
- Leave reviews (1-5 stars) for completed orders

### For Vendors
- View and claim available orders
- Create and send customized quotes with adjusted pricing
- Revise quotes based on customer feedback
- Manage orders through completion
- Update order status (in progress, ready, dispatched)
- View customer reviews and ratings

### For Administrators
- Manage users (customers, vendors, admins)
- Handle password reset requests
- View system statistics
- Monitor orders and activity

## Tech Stack
- **Backend**: Python 3.11+ with Flask 3.x
- **Database**: SQLAlchemy ORM (SQLite default, PostgreSQL supported)
- **Authentication**: Flask-Login with password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Migrations**: Flask-Migrate (Alembic)
- **Templates**: Jinja2
- **Frontend**: Responsive HTML/CSS with vanilla JavaScript

## Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url> smartprintpro
cd smartprintpro
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
# Database is created automatically on first run
# Seed pricing data
python seed_pricing.py
```

### 3. Run the Application
```bash
flask run --debug
```
Visit http://127.0.0.1:5000

### 4. Login as Admin
Default admin credentials (change these in production):
- **Email**: admin@smartprintpro.com
- **Password**: Admin@123

Override with environment variables:
```bash
export ADMIN_EMAIL="your@email.com"
export ADMIN_PASSWORD="YourStrongPassword"
export ADMIN_NAME="Your Name"
```

## Project Structure
```
smartprintpro1/
├── app.py                  # Main application & routes
├── config.py              # Configuration settings
├── extension.py           # Flask extensions
├── models.py              # Database models
├── forms.py               # WTForms definitions
├── decorators.py          # Role-based access decorators
├── seed_pricing.py        # Pricing data seeder
├── requirements.txt       # Python dependencies
├── instance/
│   └── app.db            # SQLite database (auto-created)
├── migrations/            # Database migrations
├── static/
│   └── css/
│       └── main.css      # Global styles
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── signup.html       # Registration
│   ├── login.html        # Login
│   ├── admin/            # Admin dashboard templates
│   ├── user/             # Customer templates
│   └── vendor/           # Vendor templates
└── uploads/              # File uploads storage
```

## Database Models

### User Models
- **Customer**: End users placing orders
- **Vendor**: Print shops fulfilling orders
- **Admin**: System administrators

### Order Management
- **Order**: Customer orders with vendor assignment
- **OrderItem**: Individual items in an order
- **OrderStatusHistory**: Complete audit trail

### Pricing & Quotes
- **ServicePrice**: Base pricing (min/max ranges)
- **Quote**: Price quotes from vendors
- **QuoteItem**: Item-level pricing in quotes

### Reviews
- **Review**: Customer ratings and comments

## Order Workflow

### Status Progression
```
pending → awaiting_vendor → quoted → quote_revised → accepted 
  → in_progress → ready → dispatched → completed
```

### Step-by-Step Process
1. **Customer creates order** with service items and files
2. **Vendor claims order** from available orders pool
3. **Vendor sends quote** with adjusted pricing and notes
4. **Customer reviews quote**:
   - Accept → Order begins processing
   - Request revision → Vendor sends new quote
5. **Negotiation continues** until agreement
6. **Vendor processes order** and updates status
7. **Customer confirms receipt** when delivered
8. **Customer leaves review** (rating + comment)

## Authentication & Authorization

### User Types
- **Customer**: Can create orders, review quotes, track progress, leave reviews
- **Vendor**: Can claim orders, send quotes, manage order fulfillment
- **Admin**: Full system access for user and order management

### Role-Based Access
Routes are protected using `@roles_required("customer", "vendor")` decorator.

### Password Reset
Customers and vendors can request password resets via `/forgot-password`. Admins handle resets through the admin panel.

## Configuration

### Database Options

**SQLite (Default)**
- No additional setup required
- Data stored in `instance/app.db`

**PostgreSQL**
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/smartprintpro"
flask run
```

### File Uploads
- Max file size: 50MB
- Allowed formats: PDF, DOCX, PNG, JPG, JPEG
- Storage location: `uploads/`

## Development

### Running Tests
See DEV_GUIDE.md for testing procedures.

### Adding New Features
1. Update models in `models.py`
2. Create migration: `flask db migrate -m "description"`
3. Apply migration: `flask db upgrade`
4. Add routes in `app.py`
5. Create templates in `templates/`
6. Add forms in `forms.py` if needed

### Code Organization
- **Models**: Define in `models.py`
- **Routes**: Register in `register_routes()` function in `app.py`
- **Templates**: Use Jinja2 inheritance from `base.html`
- **Forms**: Use Flask-WTF with CSRF protection
- **Static Files**: Place in `static/` directory

## Deployment

### Environment Variables
```bash
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-password
```

### Production Checklist
- [ ] Set strong `SECRET_KEY`
- [ ] Change admin password
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set up proper file storage (S3, etc.)
- [ ] Configure email for notifications
- [ ] Set up backup system
- [ ] Enable logging and monitoring
- [ ] Review security settings

## Troubleshooting

**Port already in use**
```bash
flask run -p 5050
```

**Virtual environment activation fails (Windows)**
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
./venv/Scripts/Activate.ps1
```

**Database locked**
Close any database viewers accessing `instance/app.db`

**Import errors**
Ensure virtual environment is activated and dependencies installed

## Contributing
1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/my-feature`
4. Create pull request

## License
MIT

## Support
For issues and questions, please open a GitHub issue or contact the development team.
