import sys
import subprocess
import os
import platform
import time
import shutil

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    # 1. OS Detection
    is_windows = platform.system() == "Windows"
    
    # 2. Python Executable Detection
    # Use the same python executable that is running this script
    # (This avoids the pydantic_core binary crash in the broken .venv)
    venv_python = sys.executable
        
    # 3. Node Modules Detection
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print(f"\n[ERROR] Frontend dependencies not found in {frontend_dir}/node_modules")
        print("Please navigate to the frontend folder and run 'npm install' first.")
        sys.exit(1)
        
    # 4. Check if npm exists
    npm_cmd = "npm.cmd" if is_windows else "npm"
    if not shutil.which(npm_cmd):
        print(f"\n[ERROR] npm not found on PATH. Please ensure Node.js is installed.")
        sys.exit(1)

    # 5. Launch Backend
    print("Starting backend server...")
    backend_cmd = [venv_python, "-m", "uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    try:
        backend_process = subprocess.Popen(backend_cmd, cwd=base_dir)
    except Exception as e:
        print(f"\n[ERROR] Failed to start backend: {e}")
        print("Ensure your virtual environment is set up correctly.")
        sys.exit(1)
        
    # 6. Launch Frontend
    print("Starting frontend server...")
    frontend_cmd = [npm_cmd, "run", "dev", "--", "--host"]
    try:
        frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=is_windows)
    except Exception as e:
        print(f"\n[ERROR] Failed to start frontend: {e}")
        backend_process.terminate()
        sys.exit(1)
        
    print("\n=======================================================")
    print("Both servers are starting. Check the output above for the Local and Network URLs.")
    print("Press Ctrl+C at any time to stop both servers cleanly.")
    print("=======================================================\n")
    
    # 7. Keep Alive and Handle Graceful Shutdown
    try:
        while True:
            time.sleep(1)
            # Check if either process died unexpectedly
            if backend_process.poll() is not None:
                print("\n[ERROR] Backend server stopped unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("\n[ERROR] Frontend server stopped unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    finally:
        # Terminate processes cleanly
        try:
            backend_process.terminate()
        except:
            pass
        try:
            frontend_process.terminate()
        except:
            pass
        
        backend_process.wait()
        frontend_process.wait()
        print("Servers stopped cleanly.")

if __name__ == "__main__":
    main()
