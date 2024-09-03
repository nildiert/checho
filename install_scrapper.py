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

def select_windows_user():
    # List Windows users
    users_dir = '/mnt/c/Users'
    users = [user for user in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, user)) and user != 'desktop.ini']

    # Display and select user
    print("Please select a Windows user for installation:")
    for i, user in enumerate(users, start=1):
        print(f"{i}) {user}")

    while True:
        try:
            choice = int(input("Select a user by number: "))
            if 1 <= choice <= len(users):
                return users[choice - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    install_venv()
    
    # Select the user
    win_user = select_windows_user()
    install_dir = f"/mnt/c/Users/{win_user}/Documents/scrapper"
    
    # Create installation directory
    os.makedirs(install_dir, exist_ok=True)
    
    # Navigate to installation directory
    os.chdir(install_dir)
    
    # Clone the repository
    subprocess.run(['git', 'clone', 'https://github.com/nildiert/checho.git', '.'], check=True)
    
    # Create a Python virtual environment in the installation directory
    subprocess.run(['python3', '-m', 'venv', '.venv'], check=True)
    
    # Activate the virtual environment and install dependencies
    activate_script = os.path.join(install_dir, '.venv/bin/activate')
    subprocess.run([f"bash -c 'source {activate_script} && pip install --upgrade pip && pip install -r requirements.txt'"], shell=True, check=True)
    
    # Make sure the main script is executable
    subprocess.run(['chmod', '+x', 'main.py'], check=True)
    
    print(f"Installation complete. The repository is installed in {install_dir}.")
    print(f"To activate the virtual environment, run 'source {install_dir}/.venv/bin/activate'")

if __name__ == "__main__":
    main()
