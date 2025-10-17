SmartPrint Pro

Overview
SmartPrint Pro is a minimal Flask web app that showcases a landing page for discovering local print shops. It uses Flask for routing, Jinja2 templates for HTML, and static assets (CSS/Images) served by Flask.

Key Features
- Landing page with search/filter for demo vendor cards
- Modal contact form (demo)
- Responsive layout with externalized CSS in `static/css/main.css`

Tech Stack
- Python 3.11+ (recommended)
- Flask 3.x
- Jinja2

Repository Layout
- `app.py` – Flask app entrypoint and route definitions
- `templates/index.html` – Main page template
- `static/css/main.css` – Stylesheet for the landing page
- `static/assets/images/` – Images (e.g., logo)

Quick Start (Windows, macOS, Linux)
1) Create and activate a virtual environment
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
2) Install dependencies
   ```bash
   pip install -U pip
   pip install flask psycopg2-binary
   ```
3) Run the app
   ```bash
   set FLASK_APP=app.py   # PowerShell: $env:FLASK_APP = "app.py"
   flask run --debug
   ```
   Visit http://127.0.0.1:5000

Database (Optional)
The code includes an example `connect_db()` using `psycopg2-binary`. You don't need a database to run the demo. If you want to connect to PostgreSQL, update credentials in `app.py`.

Development Notes
- Static assets are served from `static/`; use `url_for('static', filename='...')` in templates.
- Styles are centralized in `static/css/main.css`.
- For additional pages, create templates in `templates/` and routes in `app.py`.

Troubleshooting
- Port in use: change port with `flask run -p 5050`.
- Virtual environment not activating on Windows: run PowerShell as Administrator and `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.
- If `psycopg2-binary` fails on your platform, use `pip install psycopg2-binary==2.9.11` or install PostgreSQL client libraries and use `psycopg2`.

License
MIT


