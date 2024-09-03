#!/bin/bash

# Define variables
REPO_URL="https://github.com/nildiert/checho.git"
INSTALL_DIR="$HOME/Documents/checho"

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Navigate to installation directory
cd "$INSTALL_DIR"

# Clone the repository
git clone "$REPO_URL" .

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Make sure the main script is executable
chmod +x main.py

echo "Installation complete. The repository is installed in $INSTALL_DIR."
