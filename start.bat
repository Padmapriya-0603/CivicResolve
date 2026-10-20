@echo off
echo ========================================================
echo Starting CivicResolve - Public Grievance Management System
echo ========================================================

echo Starting Backend Service on port 8000...
start "CivicResolve - Backend" cmd /k "cd /d %~dp0backend && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend UI on port 5173...
start "CivicResolve - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo ========================================================
echo Both servers have been launched!
echo Access the Frontend at: http://localhost:5173
echo Access the Backend at:  http://localhost:8000
echo Access API Docs at:     http://localhost:8000/docs
echo ========================================================
