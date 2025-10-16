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
pip install flask psycopg2-binary
```

5) Verify project structure
You should have:
- `app.py`
- `templates/index.html`
- `static/css/main.css`
- `static/assets/images/` (optional images)

6) Run the development server
```powershell
$env:FLASK_APP = "app.py"
flask run --debug
```
You should see output indicating the server is running on `http://127.0.0.1:5000`.

7) Open the app
Open your browser to `http://127.0.0.1:5000`.

8) Common tasks
- Change port:
  ```powershell
  flask run -p 5050
  ```
- Add a new page: create a template in `templates/` and add a route in `app.py`.
- Add styles: edit `static/css/main.css`.
- Add images: place them under `static/assets/images/` and reference with `{{ url_for('static', filename='assets/images/your.png') }}`.

9) Optional: Connect to PostgreSQL
If you want to test DB connections, install PostgreSQL locally or use Docker, then update credentials in `connect_db()` inside `app.py`.

10) Troubleshooting
- Virtual env activation fails: ensure the execution policy change above, or use CMD: `venv\Scripts\activate.bat`.
- Flask not found: confirm the venv is active and `pip show flask` displays a version.
- Port already in use: specify a different port with `-p`.
- `psycopg2-binary` install issues: pin to `2.9.11` or install PostgreSQL client tools.


