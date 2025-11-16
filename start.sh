#!/bin/bash
# Start script for OpenAI Responses Starter App
# Starts both the backend (FastAPI) and frontend (Streamlit) servers

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=============================================================="
echo -e "OpenAI Responses Starter App"
echo -e "==============================================================${NC}\n"

# Check if directories exist
if [ ! -d "backend" ]; then
    echo -e "${RED}✗ Backend directory not found!${NC}"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo -e "${RED}✗ Frontend directory not found!${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ All servers stopped${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Start backend
echo -e "${BLUE}=============================================================="
echo -e "Starting Backend Server (FastAPI)"
echo -e "==============================================================${NC}"
cd backend
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓ Backend starting on http://localhost:8000${NC}"

# Wait a bit for backend to start
sleep 2

# Start frontend
echo -e "\n${BLUE}=============================================================="
echo -e "Starting Frontend Server (Streamlit)"
echo -e "==============================================================${NC}"
cd frontend
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend starting on http://localhost:8501${NC}"

# Wait for user interrupt
echo -e "\n${BLUE}=============================================================="
echo -e "Servers Running"
echo -e "==============================================================${NC}"
echo -e "${BLUE}Backend:  http://localhost:8000${NC}"
echo -e "${GREEN}Frontend: http://localhost:8501${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}\n"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID

