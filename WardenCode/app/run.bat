@echo off
REM Warden GUI launcher — double-click to start.
REM Installs Flask on first run if it's missing, then starts the local server.

cd /d "%~dp0"

python -c "import flask" 2>NUL
if errorlevel 1 (
    echo First run: installing Flask...
    python -m pip install -r requirements.txt
)

echo Starting Warden — opening http://127.0.0.1:5057 in your browser...
python app.py
pause
