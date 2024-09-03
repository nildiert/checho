#!/bin/bash

# Define the Python script URL
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/nildiert/checho/main/install_scrapper.py"

# Download the Python script
curl -o install_scrapper.py "$PYTHON_SCRIPT_URL"

# Make the Python script executable
chmod +x install_scrapper.py

# Run the Python script
python3 install_scrapper.py

# Clean up
rm install_scrapper.py
