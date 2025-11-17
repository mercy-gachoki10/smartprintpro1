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

This will install:
- Flask (web framework)
- Flask-SQLAlchemy (database ORM with SQLite support)
- Flask-Migrate (database migrations)
- Flask-WTF (form handling and CSRF protection)
- Flask-Login (user session management)
- bcrypt (password hashing)
- psycopg2-binary (PostgreSQL support - optional)

5) Initialize the database (first time setup)
```powershell
$env:FLASK_APP = "app.py"
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

This creates a SQLite database in `instance/app.db` with the necessary tables.

6) Verify project structure
You should have:
- `app.py`
- `requirements.txt`
- `config.py` (database configuration)
- `models.py` (database models)
- `templates/index.html`
- `static/css/main.css`
- `static/assets/images/` (optional images)
- `instance/app.db` (after database initialization)

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

**SQLite (Default):**
The application uses SQLite by default, which requires no additional setup. The database file is created in `instance/app.db` when you run migrations.

**PostgreSQL (Optional):**
To use PostgreSQL instead of SQLite:
1. Install PostgreSQL locally or use Docker
2. Update database credentials in `config.py`:
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'
   ```
3. Run migrations as usual - Flask-Migrate will use PostgreSQL instead of SQLite

12) Troubleshooting
- Virtual env activation fails: ensure the execution policy change above, or use CMD: `venv\Scripts\activate.bat`.
- Flask not found: confirm the venv is active and `pip show flask` displays a version.
- Port already in use: specify a different port with `-p`.
- `psycopg2-binary` install issues: pin to `2.9.11` or install PostgreSQL client tools.
- Database migration errors: ensure you've run `flask db init` before `flask db migrate`.
- SQLite database locked: close any database viewers or ensure no other process is accessing `instance/app.db`.


