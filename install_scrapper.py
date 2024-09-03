import os
import subprocess
import sys

def install_venv():
    # Check if python3-venv is installed, and install if necessary
    try:
        subprocess.run(['python3', '-m', 'venv', '--help'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("python3-venv is not installed. Installing it now...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'python3-venv'], check=True)

def main():
    # Ensure the script is called with the correct arguments
    if len(sys.argv) != 2:
        print("Usage: python3 install_scrapper.py <Windows_Username>")
        sys.exit(1)

    win_user = sys.argv[1]
    install_venv()
    
    install_dir = f"/mnt/c/Users/{win_user}/Documents/scrapper"
    
    # Create installation directory
    os.makedirs(install_dir, exist_ok=True)
    
    # Navigate to installation directory
    os.chdir(install_dir)
    
    # Clone the repository
    subprocess.run(['git', 'clone', 'https://github.com/nildiert/checho.git', '.'], check=True)
    
    # Create and activate a Python virtual environment in the installation directory
    subprocess.run(['python3', '-m', 'venv', '.venv'], check=True)
    activate_script = os.path.join(install_dir, '.venv/bin/activate')
    
    # Install dependencies
    subprocess.run([f"source {activate_script} && pip install --upgrade pip && pip install -r requirements.txt"], shell=True, check=True)
    
    # Make sure the main script is executable
    subprocess.run(['chmod', '+x', 'main.py'], check=True)
    
    print(f"Installation complete. The repository is installed in {install_dir}.")
    print(f"To activate the virtual environment, run 'source {install_dir}/.venv/bin/activate'")

if __name__ == "__main__":
    main()
