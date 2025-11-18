Windows Developer Guide

This guide walks through setting up the project on Windows 10/11 step by step.

Prerequisites
- Windows 10/11
- Python 3.11 or newer added to PATH (check with `python --version`)
- PowerShell (recommended) or Command Prompt

1) Clone or download the repository
If you have Git:
```powershell
git clone <your-repo-url> smartprint-pro
cd smartprint-pro
```
Otherwise, download the ZIP, extract it, and open the folder in PowerShell.

2) Create a virtual environment
```powershell
python -m venv venv
```

3) Activate the virtual environment
```powershell
./venv/Scripts/Activate.ps1
```
If you see an execution policy error, run PowerShell as Administrator once and execute:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Then re-run the activation command.

4) Upgrade pip and install dependencies
```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

This installs Flask plus the extensions used for authentication (`Flask-WTF`, `Flask-Login`, `Flask-SQLAlchemy`, etc.).

5) Initialize the database (first time setup)

Tables are created automatically the first time you run `flask run`. Once the schema stabilizes you can also use Flask-Migrate:
```powershell
$env:FLASK_APP = "app.py"
flask db init                # once
flask db migrate -m "initial"
flask db upgrade
```

6) Verify project structure
You should have (partial list):
- `app.py` (application factory + routes)
- `config.py` (SQLite/PostgreSQL config)
- `extension.py` (db/migrate/login manager instances)
- `models.py` (customer, staff, admin tables)
- `forms.py` (registration + login forms)
- `decorators.py` (role guard)
- `templates/` (marketing pages + dashboards + auth pages)
- `static/css/main.css`
- `instance/app.db` (created on first run)

6.5) Prepare the database (recommended before `flask run`)
```powershell
$env:FLASK_APP = "app.py"
flask db init          # only the first time
flask db migrate -m "initial structure"
flask db upgrade
```

7) Run the development server
```powershell
$env:FLASK_APP = "app.py"
flask run --debug
```
You should see output indicating the server is running on `http://127.0.0.1:5000`.

8) Open the app
Open your browser to `http://127.0.0.1:5000`.

9) Common tasks
- Change port:
  ```powershell
  flask run -p 5050
  ```
- Add a new page: create a template in `templates/` and add a route in `app.py`.
- Add styles: edit `static/css/main.css`.
- Add images: place them under `static/assets/images/` and reference with `{{ url_for('static', filename='assets/images/your.png') }}`.

10) Git Workflow: Creating and Merging Branches
**Create a new branch for your feature:**
```powershell
git switch -c feature/my-feature
# or if using older Git: git checkout -b feature/my-feature
```

**Make your changes and commit:**
```powershell
git add .
git commit -m "Description of changes"
```

**Push your branch to the remote repository:**
```powershell
git push -u origin feature/my-feature
```

**Merge your branch back to main (after code review/testing):**
```powershell
# Switch to main branch
git switch main
# or: git checkout main

# Pull latest changes from remote
git pull origin main

# Merge your feature branch
git merge feature/my-feature

# Push the merged changes
git push origin main

# (Optional) Delete the feature branch locally and remotely
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

11) Database Configuration

**SQLite (Default)**
- No setup needed. Data is stored in `instance/app.db`.

**PostgreSQL (Optional)**
1. Install PostgreSQL locally or run a Docker container.
2. Export `DATABASE_URL` before running Flask, e.g.
   ```powershell
   $env:DATABASE_URL = "postgresql://user:password@localhost:5432/smartprintpro"
   ```
3. Run `flask db upgrade` (or let `db.create_all()` run on launch) to create the tables.

**Admin seeding**
- The first `flask run` call seeds a default administrator (`admin@smartprintpro.com` / `Admin@123`) if one does not exist.
- Override with environment variables:
  ```powershell
  $env:ADMIN_EMAIL = "you@example.com"
  $env:ADMIN_PASSWORD = "StrongPass123"
  ```

**Authentication workflow**
- `/signup`: create customer or staff accounts (admins are seeded, not self-registered).
- `/login`: email/password only — the backend automatically figures out the user type.
- `/dashboard`: redirects to the correct dashboard template based on the role.

12) Troubleshooting
- Virtual env activation fails: ensure the execution policy change above, or use CMD: `venv\Scripts\activate.bat`.
- Flask not found: confirm the venv is active and `pip show flask` displays a version.
- Port already in use: specify a different port with `-p`.
- `psycopg2-binary` install issues: pin to `2.9.11` or install PostgreSQL client tools.
- Database migration errors: ensure you've run `flask db init` before `flask db migrate`.
- SQLite database locked: close any database viewers or ensure no other process is accessing `instance/app.db`.


