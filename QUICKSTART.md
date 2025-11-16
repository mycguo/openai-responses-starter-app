# Quick Start Guide

This guide will help you get the OpenAI Responses Starter App running quickly.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- (Optional) Google OAuth credentials for Google integration

## Quick Start (Easiest Method)

### Option 1: Use the Start Script (Recommended)

**Python Script (Cross-platform):**
```bash
python start.py
```

**Shell Script (Linux/Mac):**
```bash
./start.sh
```

**Batch Script (Windows):**
```batch
start.bat
```

The script will:
- ✅ Check dependencies
- ✅ Check API key configuration
- ✅ Start backend server (port 8000)
- ✅ Start frontend server (port 8501)
- ✅ Monitor both processes
- ✅ Stop both when you press Ctrl+C

### Option 2: Manual Setup

### 1. Install Dependencies

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
pip install -r requirements.txt
cd ..
```

### 2. Set API Keys

**Option A: Streamlit Secrets (Recommended)**

Create `.streamlit/secrets.toml`:
```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id  # Optional
GOOGLE_CLIENT_SECRET=your_google_client_secret  # Optional
GOOGLE_REDIRECT_URI=http://localhost:8501/api/google/callback
NODE_ENV=development
EOF
```

**Option B: Environment Variables**

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start Servers Manually

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

### 4. Open the App

Open your browser and navigate to:
```
http://localhost:8501
```

## Verify Everything is Working

1. **Check Backend Health:**
   - Visit `http://localhost:8000/health` in your browser
   - You should see: `{"status":"ok"}`

2. **Check Backend Root:**
   - Visit `http://localhost:8000/` in your browser
   - You should see: `{"message":"OpenAI Responses Starter App Backend"}`

3. **Test the Frontend:**
   - Open `http://localhost:8501`
   - You should see the chat interface
   - Try sending a message to test the connection

## Troubleshooting

### Backend won't start

- **Error: "Module not found"**
  - Make sure you installed dependencies: `pip install -r requirements.txt`
  - Make sure you're in the `backend` directory

- **Error: "Address already in use"**
  - Port 8000 is already in use
  - Change the port: `uvicorn main:app --reload --port 8001`
  - Update `API_BASE_URL` in frontend to match

- **Error: "OPENAI_API_KEY not found"**
  - Make sure you created the `.env` file in the `backend` directory
  - Check that the `.env` file has the correct format

### Frontend won't connect to backend

- **Error: "Connection refused"**
  - Make sure the backend is running on port 8000
  - Check that `API_BASE_URL` is set correctly (defaults to `http://localhost:8000`)

- **CORS errors**
  - Make sure the backend CORS is configured for `http://localhost:8501`
  - Check `backend/main.py` CORS configuration

### Streamlit won't start

- **Error: "Module not found"**
  - Make sure you installed dependencies: `pip install -r requirements.txt`
  - Make sure you're in the `frontend` directory

## Running in Production

For production deployment:

1. **Backend:**
   ```bash
   # Use gunicorn with uvicorn workers
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Frontend:**
   - Deploy to Streamlit Cloud, or
   - Use a reverse proxy (nginx) in front of Streamlit

3. **Environment Variables:**
   - Set all environment variables securely
   - Use a secrets management system
   - Never commit `.env` files

## Next Steps

- Configure tools in the sidebar (File Search, Web Search, etc.)
- Upload files to create vector stores
- Connect Google integration (if configured)
- Start chatting with the assistant!

