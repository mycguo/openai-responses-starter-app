# Quick Start Guide

The easiest way to start the application is using the provided start scripts.

## Quick Start (One Command)

### Python Script (Cross-platform - Recommended)

```bash
python start.py
```

This will:
- ✅ Check if dependencies are installed
- ✅ Check API key configuration
- ✅ Start backend server on port 8000
- ✅ Start frontend server on port 8501
- ✅ Monitor both processes
- ✅ Stop both when you press Ctrl+C

### Shell Script (Linux/Mac)

```bash
./start.sh
```

### Batch Script (Windows)

```batch
start.bat
```

## Prerequisites

Before running the start script, make sure you have:

1. **Installed dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

2. **Configured API keys:**

   **Option A: Streamlit Secrets (Recommended)**
   ```bash
   mkdir -p .streamlit
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml and add your API keys
   ```

   **Option B: Environment Variables**
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   ```

## What the Script Does

1. **Checks Dependencies**
   - Verifies uvicorn and streamlit are installed
   - Shows helpful error messages if missing

2. **Checks API Key**
   - Looks for Streamlit secrets file
   - Checks environment variables
   - Shows warning if not found (but continues)

3. **Starts Backend**
   - Runs FastAPI server on port 8000
   - Enables auto-reload for development

4. **Starts Frontend**
   - Runs Streamlit app on port 8501
   - Opens in your default browser

5. **Monitors Processes**
   - Watches both servers
   - Stops both if one crashes
   - Handles Ctrl+C gracefully

## Output

When you run the script, you'll see:

```
==============================================================
OpenAI Responses Starter App
==============================================================

Checking dependencies...
✓ All dependencies found
Checking API key configuration...
✓ Found Streamlit secrets file

==============================================================
Starting Backend Server (FastAPI)
==============================================================
✓ Backend starting on http://localhost:8000

==============================================================
Starting Frontend Server (Streamlit)
==============================================================
✓ Frontend starting on http://localhost:8501

==============================================================
Servers Running
==============================================================
Backend:  http://localhost:8000
Frontend: http://localhost:8501

Press Ctrl+C to stop all servers
```

## Stopping the Servers

Press **Ctrl+C** in the terminal where you ran the script. Both servers will stop gracefully.

## Troubleshooting

### "Module not found" error

Install dependencies:
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Port already in use

If port 8000 or 8501 is already in use:

1. **Stop the existing process:**
   ```bash
   # Find process using port 8000
   lsof -ti:8000 | xargs kill
   
   # Find process using port 8501
   lsof -ti:8501 | xargs kill
   ```

2. **Or modify the scripts** to use different ports

### API key not found

The script will show a warning but continue. Make sure to:
- Create `.streamlit/secrets.toml` with your API keys, or
- Set `OPENAI_API_KEY` environment variable

## Manual Start (Alternative)

If you prefer to start servers manually or need more control:

**Terminal 1:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2:**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

## Production Deployment

For production, don't use the start script. Instead:

1. **Backend:** Use a production ASGI server like Gunicorn
2. **Frontend:** Deploy to Streamlit Cloud or use a reverse proxy

See individual README files in `backend/` and `frontend/` directories for production deployment instructions.

