#!/bin/bash

# Define the Python script URL
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/nildiert/checho/main/install_scrapper.py"

# Download the Python script to the current directory
curl -O "$PYTHON_SCRIPT_URL"

echo "The installation script has been downloaded as install_scrapper.py."
echo "You can now run it with: python3 install_scrapper.py"
