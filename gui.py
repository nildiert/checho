import sys
import subprocess
try:
    import customtkinter as ctk
    from tkinter import filedialog
except ModuleNotFoundError:
    print(
        "No se encontró el módulo tkinter requerido para la interfaz gráfica.\n"
        "Instala las dependencias de Tk con uno de los siguientes comandos:\n"
        "  macOS: brew install python-tk\n"
        "  Ubuntu/WSL: sudo apt-get install python3-tk"
    )
    sys.exit(1)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Descargar información")

excel_path = ctk.StringVar()


def choose_file():
    path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if path:
        excel_path.set(path)


skip_var = ctk.BooleanVar()
square_var = ctk.BooleanVar()


def run_main():
    cmd = [sys.executable, "main.py"]
    if skip_var.get():
        cmd.append("--skip-download")
    if square_var.get():
        cmd.append("--imagenes-cuadradas")
    if excel_path.get():
        cmd.extend(["--excel-file", excel_path.get()])
    subprocess.run(cmd)


file_button = ctk.CTkButton(app, text="Cargar archivo de Excel", command=choose_file)
file_button.pack(pady=10)

file_label = ctk.CTkLabel(app, textvariable=excel_path)
file_label.pack(pady=5)

skip_checkbox = ctk.CTkCheckBox(app, text="Omitir descarga", variable=skip_var)
skip_checkbox.pack(pady=5)

square_checkbox = ctk.CTkCheckBox(app, text="Imágenes cuadradas", variable=square_var)
square_checkbox.pack(pady=5)

run_button = ctk.CTkButton(app, text="Descargar información", command=run_main)
run_button.pack(pady=20)

app.mainloop()
