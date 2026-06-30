import sys
import subprocess
import os
import platform
import time
import shutil
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # connect to an external IP to find the local IP used for routing
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

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
        
    # 6. Update Frontend .env with Local IP
    local_ip = get_local_ip()
    env_path = os.path.join(frontend_dir, ".env")
    try:
        with open(env_path, "w") as f:
            f.write(f"VITE_API_URL=http://{local_ip}:8000\n")
        print(f"\nDetected network IP: {local_ip}")
        print(f"Frontend will be accessible at http://{local_ip}:5173")
    except Exception as e:
        print(f"\n[WARNING] Could not update {env_path}: {e}")

    # 7. Launch Frontend
    print("Starting frontend server...")
    frontend_cmd = [npm_cmd, "run", "dev", "--", "--host"]
    try:
        frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=is_windows)
    except Exception as e:
        print(f"\n[ERROR] Failed to start frontend: {e}")
        backend_process.terminate()
        sys.exit(1)
        
    print("\n=======================================================")
    print("Both servers are starting.")
    print(f"\nChatbot is accessible locally at:   http://localhost:5173")
    print(f"Chatbot is accessible on network at: http://{local_ip}:5173")
    print("\nPress Ctrl+C at any time to stop both servers cleanly.")
    print("=======================================================\n")
    
    # 8. Keep Alive and Handle Graceful Shutdown
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
