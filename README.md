# Checho

This project processes promotional images. A small GUI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) allows you to run `main.py` with optional flags and choose a custom Excel file.

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Tkinter support is available:
   - **macOS**: install the `python-tk` formula that matches your Python version.
     Check your version with `python3 --version` and then run, for example:
     ```bash
     brew install python-tk@3.12
     ```
     Make sure to execute the GUI with the same interpreter, e.g. `python3.12 gui.py`.
   - **Ubuntu / WSL**:
     ```bash
     sudo apt-get install python3-tk
     ```

## Usage

Run the GUI:
```bash
python3 gui.py
```
The interface provides a button to select the Excel file and checkboxes for "Omitir descarga" and "Imágenes cuadradas".
