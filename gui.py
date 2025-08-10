import sys
import subprocess
import threading
import re
try:
    import customtkinter as ctk
    from tkinter import filedialog
except ModuleNotFoundError:
    print(
        "No se encontró el módulo tkinter requerido para la interfaz gráfica.\n"
        "Instala las dependencias de Tk con uno de los siguientes comandos:\n"
        "  macOS: brew install python-tk@<versión>  # usa la misma versión que tu Python, por ejemplo 3.12\n"
        "  Ubuntu/WSL: sudo apt-get install python3-tk\n"
        "Tras instalarlo, ejecuta gui.py con la misma versión de Python\n"
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
    cmd = [sys.executable, "-u", "main.py"]
    if skip_var.get():
        cmd.append("--skip-download")
    if square_var.get():
        cmd.append("--imagenes-cuadradas")
    if excel_path.get():
        cmd.extend(["--excel-file", excel_path.get()])

    progress_bar.set(0)
    run_button.configure(state="disabled")

    def worker():
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
            for line in proc.stdout:
                match = re.search(r"(\d+)%", line)
                if match:
                    percent = int(match.group(1)) / 100
                    app.after(0, progress_bar.set, percent)
            proc.wait()
        app.after(0, progress_bar.set, 1)
        app.after(0, run_button.configure, {"state": "normal"})

    threading.Thread(target=worker, daemon=True).start()


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

progress_bar = ctk.CTkProgressBar(app, width=300)
progress_bar.pack(pady=10)
progress_bar.set(0)

app.mainloop()
