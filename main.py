import os
import sys
import subprocess
import venv
import shutil
import platform

def setup_dependencies():
    if not shutil.which("kubescape"):
        print("Kubescape not found. Attempting auto-installation...")
        try:
            if platform.system() != "Windows":
                subprocess.run(
                    "curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash", 
                    shell=True, check=True
                )
                print("Kubescape installed.")
            else:
                print("Kubescape will need to be installed manually.")
        except Exception as e:
            print(f"Filed to install Kubescape: {e}")

    venv_dir = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
    
    # python_exe = os.path.join(venv_dir, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(venv_dir, "bin", "python")
    subprocess.run(["python", "-m", "pip", "install", "transformers", "datasets", "evaluate", "accelerate", "torch"], check=True)
    subprocess.run(["python", "-m", "pip", "install", "ollama", "pdfplumber", "PyYAML", "pandas"], check=True)
    return "python"

def run():
    python_path = setup_dependencies()
    subprocess.run([python_path, "project_task1.py"], check=True)
    subprocess.run([python_path, "project_task2.py"], check=True)
    subprocess.run([python_path, "project_task3.py"], check=True)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"\nError during execution: {e}")