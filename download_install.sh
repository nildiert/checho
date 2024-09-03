#!/bin/bash

# Define the Python script URL
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/nildiert/checho/main/install_scrapper.py"

# Download the Python script to the current directory
curl -O "$PYTHON_SCRIPT_URL"

echo "El script de instalación se ha descargado como install_scrapper.py."
echo "Ahora puedes ejecutarlo con: python3 install_scrapper.py"

# Define the alias to be added
alias_command="alias install_scrapper='python3 $(pwd)/install_scrapper.py'"

# Add the alias to ~/.bashrc
echo "$alias_command" >> ~/.bashrc

# Apply the changes to the current terminal session
source ~/.bashrc

echo "Escribe en la consola 'source ~/.bashrc' para que puedas usar el comando 'install_scrapper'"
