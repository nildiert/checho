# Checho

This project processes promotional images. A small GUI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) allows you to run `main.py` with optional flags and choose a custom Excel file.

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Tkinter support is available:
   - **macOS**:
     ```bash
     brew install python-tk
     ```
   - **Ubuntu / WSL**:
     ```bash
     sudo apt-get install python3-tk
     ```

## Usage

Run the GUI:
```bash
python gui.py
```
The interface provides a button to select the Excel file and checkboxes for "Omitir descarga" and "Imágenes cuadradas".
