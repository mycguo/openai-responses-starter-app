#!/usr/bin/env python3
"""
Start script for OpenAI Responses Starter App
Starts both the backend (FastAPI) and frontend (Streamlit) servers
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.END):
    """Print colored message"""
    print(f"{color}{message}{Colors.END}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print_colored("Checking dependencies...", Colors.BLUE)
    
    try:
        import uvicorn
        import streamlit
        print_colored("✓ All dependencies found", Colors.GREEN)
        return True
    except ImportError as e:
        print_colored(f"✗ Missing dependency: {e}", Colors.RED)
        print_colored("Please install dependencies:", Colors.YELLOW)
        print_colored("  pip install -r backend/requirements.txt", Colors.YELLOW)
        print_colored("  pip install -r frontend/requirements.txt", Colors.YELLOW)
        return False

def check_api_key():
    """Check if API key is configured"""
    print_colored("Checking API key configuration...", Colors.BLUE)
    
    # Check Streamlit secrets
    secrets_file = Path(".streamlit/secrets.toml")
    if secrets_file.exists():
        print_colored("✓ Found Streamlit secrets file", Colors.GREEN)
        return True
    
    # Check environment variable
    if os.getenv("OPENAI_API_KEY"):
        print_colored("✓ Found OPENAI_API_KEY in environment", Colors.GREEN)
        return True
    
    print_colored("⚠ No API key found in secrets or environment", Colors.YELLOW)
    print_colored("  The app may not work without OPENAI_API_KEY", Colors.YELLOW)
    print_colored("  Create .streamlit/secrets.toml or set OPENAI_API_KEY environment variable", Colors.YELLOW)
    return False

def start_backend():
    """Start the FastAPI backend server"""
    print_colored("\n" + "="*60, Colors.BOLD)
    print_colored("Starting Backend Server (FastAPI)", Colors.BOLD)
    print_colored("="*60, Colors.END)
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_colored("✗ Backend directory not found!", Colors.RED)
        return None
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start uvicorn server
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Go back to project root
    os.chdir("..")
    
    return process

def start_frontend():
    """Start the Streamlit frontend server"""
    print_colored("\n" + "="*60, Colors.BOLD)
    print_colored("Starting Frontend Server (Streamlit)", Colors.BOLD)
    print_colored("="*60, Colors.END)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_colored("✗ Frontend directory not found!", Colors.RED)
        return None
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Start streamlit server
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Go back to project root
    os.chdir("..")
    
    return process

def print_output(process, name, color):
    """Print output from a process"""
    if process:
        for line in process.stdout:
            print_colored(f"[{name}] {line.rstrip()}", color)

def main():
    """Main function"""
    print_colored("\n" + "="*60, Colors.BOLD)
    print_colored("OpenAI Responses Starter App", Colors.BOLD)
    print_colored("="*60 + "\n", Colors.END)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check API key (warning only)
    check_api_key()
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        if backend_process:
            processes.append(("Backend", backend_process, Colors.BLUE))
            print_colored("✓ Backend starting on http://localhost:8000", Colors.GREEN)
            time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(("Frontend", frontend_process, Colors.GREEN))
            print_colored("✓ Frontend starting on http://localhost:8501", Colors.GREEN)
        
        if not processes:
            print_colored("✗ Failed to start any servers", Colors.RED)
            sys.exit(1)
        
        print_colored("\n" + "="*60, Colors.BOLD)
        print_colored("Servers Running", Colors.BOLD)
        print_colored("="*60, Colors.END)
        print_colored("Backend:  http://localhost:8000", Colors.BLUE)
        print_colored("Frontend: http://localhost:8501", Colors.GREEN)
        print_colored("\nPress Ctrl+C to stop all servers\n", Colors.YELLOW)
        
        # Monitor processes
        while True:
            for name, process, color in processes:
                if process.poll() is not None:
                    print_colored(f"\n✗ {name} process exited unexpectedly", Colors.RED)
                    # Stop all processes
                    for n, p, c in processes:
                        if p.poll() is None:
                            p.terminate()
                    sys.exit(1)
            time.sleep(1)
    
    except KeyboardInterrupt:
        print_colored("\n\nStopping servers...", Colors.YELLOW)
        for name, process, color in processes:
            if process.poll() is None:
                print_colored(f"Stopping {name}...", Colors.YELLOW)
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print_colored("✓ All servers stopped", Colors.GREEN)
        sys.exit(0)

if __name__ == "__main__":
    main()

