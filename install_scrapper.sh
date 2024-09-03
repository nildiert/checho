#!/bin/bash

# Define the Python script URL
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/nildiert/checho/main/install_scrapper.py"

# Download the Python script
curl -o install_scrapper.py "$PYTHON_SCRIPT_URL"

# Make the Python script executable
chmod +x install_scrapper.py

# List Windows users and prompt for selection
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

# Run the Python script with the selected user as an argument
python3 install_scrapper.py "$WIN_USER"

# Clean up
rm install_scrapper.py
