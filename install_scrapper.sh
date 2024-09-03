#!/bin/bash

if ! dpkg -l | grep -q python3-venv; then
    echo "python3-venv is not installed. Installing it now..."
    sudo apt update
    sudo apt install -y python3-venv
fi

echo "Please select a Windows user for installation:"
users=$(ls /mnt/c/Users)
select WIN_USER in $users; do
    if [ -n "$WIN_USER" ]; then
        echo "You selected $WIN_USER"
        break
    else
        echo "Invalid selection. Please try again."
    fi
done

INSTALL_DIR="/mnt/c/Users/$WIN_USER/Documents/scrapper"

mkdir -p "$INSTALL_DIR"

cd "$INSTALL_DIR"

git clone https://github.com/nildiert/checho.git .

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

chmod +x main.py

echo "Installation complete. The repository is installed in $INSTALL_DIR."
echo "To activate the virtual environment, run 'source $INSTALL_DIR/.venv/bin/activate'"
