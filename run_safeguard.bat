@echo off
echo Checking requirements...

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please download it from: https://www.python.org/downloads/
    pause
    exit /b
)

node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in your PATH!
    echo Please download it from: https://nodejs.org/en/download/
    pause
    exit /b
)

echo.
echo Installing Backend dependencies...
pip install -r requirements.txt

echo.
echo Starting Backend Server in a new window...
start cmd /k "cd backend && python main.py"

echo.
echo Installing Frontend dependencies...
cd frontend
call npm install

echo.
echo Starting Frontend Server in a new window...
start cmd /k "npm run dev"

echo.
echo Everything should be starting up now!
echo A browser window will open automatically, or you can go to http://localhost:5173
pause
