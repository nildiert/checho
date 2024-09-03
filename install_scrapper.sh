#!/bin/bash

# Check if python3-venv is installed, and install if necessary
if ! dpkg -l | grep -q python3-venv; then
    echo "python3-venv is not installed. Installing it now..."
    sudo apt update
    sudo apt install -y python3-venv
fi

# List Windows users and clean up the output
echo "Please select a Windows user for installation:"
users=$(ls /mnt/c/Users | grep -v "desktop.ini")
PS3='Select a user by number: '

select WIN_USER in $users; do
    if [ -n "$WIN_USER" ]; then
        echo "You selected $WIN_USER"
        break
    else
        echo "Invalid selection. Please try again."
    fi
done

# Define the installation directory in the selected user's Documents folder
INSTALL_DIR="/mnt/c/Users/$WIN_USER/Documents/scrapper"

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Navigate to installation directory
cd "$INSTALL_DIR"

# Clone the repository
git clone https://github.com/nildiert/checho.git .

# Create and activate a Python virtual environment in the installation directory
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make sure the main script is executable
chmod +x main.py

echo "Installation complete. The repository is installed in $INSTALL_DIR."
echo "To activate the virtual environment, run 'source $INSTALL_DIR/.venv/bin/activate'"
