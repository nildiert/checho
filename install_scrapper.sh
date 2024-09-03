#!/bin/bash

REPO_URL="https://github.com/nildiert/checho.git"
INSTALL_DIR="$HOME/Documents/checho"

mkdir -p "$INSTALL_DIR"

cd "$INSTALL_DIR"

git clone "$REPO_URL" .

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

chmod +x main.py

echo "Installation complete. The repository is installed in $INSTALL_DIR."
echo "To activate the virtual environment, run 'source $INSTALL_DIR/.venv/bin/activate'"
