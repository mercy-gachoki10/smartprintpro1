SmartPrint Pro
==============

Overview
--------
SmartPrint Pro is a multi-role Flask web app that showcases a marketing site for local print shops **and** provides authenticated dashboards for customers, staff, and administrators. It uses Flask blueprints, Jinja2 templates, and Flask-WTF forms backed by SQLAlchemy models.

Key Features
------------
- Marketing pages (`/`, `/vendors`, `/features`, `/how-it-works`)
- Email/password authentication with hashed credentials
- Separate tables for customers, staff, and admins with role-aware dashboards
- Dynamic header/footer that react to the current session (welcome message + logout)
- Flash messaging for sign-up/sign-in feedback
- Responsive layout (see `static/css/main.css`)

Tech Stack
----------
- Python 3.11+
- Flask 3.x + Jinja2
- Flask-SQLAlchemy & Flask-Migrate
- Flask-WTF for CSRF-protected forms
- Flask-Login for session management
- Werkzeug password hashing (bcrypt-strength)
- psycopg2-binary (optional PostgreSQL driver)

Repository Layout
-----------------
- `app.py` – application factory, route registration, and seeding logic
- `config.py` – environment-aware configuration (SQLite by default, PostgreSQL via `DATABASE_URL`)
- `extension.py` – extension instances (db, migrate, login manager)
- `models.py` – user tables (`customers`, `staff_members`, `admins`)
- `forms.py` – WTForms definitions for registration and login
- `decorators.py` – role guard helpers
- `templates/` – Jinja templates (marketing pages + dashboards + auth views)
- `static/css/main.css` – global stylesheet
- `instance/app.db` – SQLite database (auto-created)

Quick Start (Windows, macOS, Linux)
-----------------------------------
1. **Create & activate a virtual environment**
   - Windows (PowerShell):
     ```powershell
     python -m venv venv
     ./venv/Scripts/Activate.ps1
     ```
   - macOS/Linux (bash):
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
2. **Install dependencies**
   ```bash
   pip install -U pip
   pip install -r requirements.txt
   ```
3. **Run the app**
   ```bash
   # PowerShell
   $env:FLASK_APP = "app.py"
   flask run --debug
   ```
   Visit http://127.0.0.1:5000

Authentication Workflow
-----------------------
1. **Sign up** as a customer or staff member at `/signup`. Successful submissions flash a success message and redirect to `/login`.
2. **Log in** at `/login`. The backend automatically discovers the correct table, verifies the hashed password, and stores the session with Flask-Login.
3. **Dashboards**:
   - Customers → `templates/user/userdash.html`
   - Staff → `templates/staff/staffdash.html`
   - Admins → `templates/admin/admindash.html`
   Each page currently displays a welcome message and role badge (functionality to be expanded later).
4. **Logout** from the header link, which clears the session and returns the user to `/login`.

Default Admin Credentials
-------------------------
The first `flask run` automatically seeds an administrator (if missing):
- Email: `admin@smartprintpro.com`
- Password: `Admin@123`

Override any of these via environment variables before launching:

```powershell
$env:ADMIN_EMAIL = "you@example.com"
$env:ADMIN_PASSWORD = "StrongPass123"
$env:ADMIN_NAME = "Jane Admin"
```

Database & Configuration
------------------------
- **SQLite**: default storage, lives at `instance/app.db`.
- **PostgreSQL**: set `DATABASE_URL` before running Flask, e.g.
  ```
  postgresql://user:pass@localhost:5432/smartprintpro
  ```
- Migrations (optional, but recommended once schemas stabilize):
  ```bash
  flask db init          # once
  flask db migrate -m "initial"
  flask db upgrade
  ```

Development Notes
-----------------
- Static assets live under `static/`; reference them with `url_for('static', filename='css/main.css')`.
- To add new pages, create templates and register new routes inside `register_routes()` in `app.py`.
- `decorators.py` exposes `@roles_required(...)` for role-scoped views beyond the shared `/dashboard`.

Troubleshooting
---------------
- Port in use → `flask run -p 5050`.
- Virtualenv fails to activate on Windows → run PowerShell as admin and `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- PostgreSQL driver issues → pin `psycopg2-binary==2.9.11` or install native libraries.
- Admin seeding not running → ensure `flask run` executes with a writeable `instance/` folder.

License
-------
MIT
