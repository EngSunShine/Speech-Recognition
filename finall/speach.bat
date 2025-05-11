@echo off
:: Check for administrative permissions
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~fnx0\"' -Verb RunAs"
    exit
)

:: Change to the project directory
cd /d C:\xampp\htdocs\speech

:: Activate virtual environment
call venv\Scripts\activate

:: Run the Python app
python app.py

:: Keep the window open
pause
