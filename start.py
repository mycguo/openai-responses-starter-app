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

try:
    import requests
except ImportError:
    requests = None

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

def wait_for_backend(url, max_attempts=30, delay=1):
    """Wait for backend to be ready"""
    if requests is None:
        # If requests is not available, just wait a fixed time
        print_colored("  (requests not available, waiting 5 seconds...)", Colors.YELLOW)
        time.sleep(5)
        return True
    
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            if i % 5 == 0:  # Print progress every 5 attempts
                print_colored(f"  Waiting... ({i+1}/{max_attempts})", Colors.YELLOW)
        time.sleep(delay)
    return False

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
        print_colored("  pip install -r requirements.txt", Colors.YELLOW)
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
    # Don't capture output so errors are visible in terminal
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        # stdout and stderr go to terminal for visibility
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
    # Don't capture output so errors are visible in terminal
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        # stdout and stderr go to terminal for visibility
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
    
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        if backend_process:
            processes.append(("Backend", backend_process, Colors.BLUE))
            print_colored("✓ Backend starting on http://localhost:8000", Colors.GREEN)
            
            # Give backend a moment to start
            time.sleep(1)
            
            # Wait for backend to be ready
            print_colored("Waiting for backend to be ready...", Colors.BLUE)
            backend_ready = wait_for_backend("http://localhost:8000/health", max_attempts=30)
            if backend_ready:
                print_colored("✓ Backend is ready", Colors.GREEN)
            else:
                print_colored("⚠ Backend may not be ready yet - check for errors above", Colors.YELLOW)
                # Check if process is still running
                if backend_process.poll() is not None:
                    print_colored("✗ Backend process exited! Check errors above.", Colors.RED)
                    print_colored("  Common issues:", Colors.YELLOW)
                    print_colored("  - Missing dependencies: pip install -r requirements.txt", Colors.YELLOW)
                    print_colored("  - Missing API key: Set OPENAI_API_KEY in .streamlit/secrets.toml or environment", Colors.YELLOW)
                    print_colored("  - Port 8000 already in use", Colors.YELLOW)
        
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

