@echo off
REM Start script for OpenAI Responses Starter App (Windows)
REM Starts both the backend (FastAPI) and frontend (Streamlit) servers

echo ==============================================================
echo OpenAI Responses Starter App
echo ==============================================================
echo.

REM Check if directories exist
if not exist "backend" (
    echo Backend directory not found!
    exit /b 1
)

if not exist "frontend" (
    echo Frontend directory not found!
    exit /b 1
)

REM Start backend
echo ==============================================================
echo Starting Backend Server (FastAPI)
echo ==============================================================
cd backend
start "Backend Server" cmd /k "python -m uvicorn main:app --reload --port 8000"
cd ..
echo Backend starting on http://localhost:8000
timeout /t 2 /nobreak >nul

REM Start frontend
echo.
echo ==============================================================
echo Starting Frontend Server (Streamlit)
echo ==============================================================
cd frontend
start "Frontend Server" cmd /k "streamlit run app.py --server.port 8501"
cd ..
echo Frontend starting on http://localhost:8501

echo.
echo ==============================================================
echo Servers Running
echo ==============================================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Close the command windows to stop the servers
echo.
pause

