#!/usr/bin/env python3
"""
Setup script for OpenAI Responses Starter App
Installs Python dependencies and Playwright browsers
"""
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description} failed")
        print(f"   {e.stderr}")
        return False

def main():
    print("🚀 Setting up OpenAI Responses Starter App...")
    print("")
    
    # Check if virtual environment exists
    import os
    venv_path = ".venv"
    use_venv = os.path.exists(venv_path) and os.path.exists(os.path.join(venv_path, "bin", "python"))
    
    if use_venv:
        print("📦 Virtual environment detected (.venv)")
        python_cmd = os.path.join(venv_path, "bin", "python")
        pip_cmd = os.path.join(venv_path, "bin", "pip")
    else:
        python_cmd = "python"
        pip_cmd = "pip"
    
    # Install Python dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)
    
    print("")
    
    # Install Playwright browsers (use the same Python as dependencies)
    if not run_command(f"{python_cmd} -m playwright install chromium", "Installing Playwright browsers"):
        print("⚠️  Warning: Playwright browser installation failed")
        print(f"   You can install manually later with: {python_cmd} -m playwright install chromium")
        sys.exit(1)
    
    print("")
    print("✅ Setup complete!")
    print("")
    print("To start the app, run:")
    print("  python start.py")
    print("")
    print("Or start manually:")
    print("  Backend:  cd backend && uvicorn main:app --reload --port 8000")
    print("  Frontend: cd frontend && streamlit run app.py --server.port 8501")

if __name__ == "__main__":
    main()

