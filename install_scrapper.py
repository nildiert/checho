import os
import subprocess
import sys

def install_venv():
    # Verifica si python3-venv está instalado, e instálalo si es necesario
    try:
        subprocess.run(['python3', '-m', 'venv', '--help'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("python3-venv no está instalado. Instalándolo ahora...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'python3-venv'], check=True)

def select_windows_user():
    # Lista los usuarios de Windows
    users_dir = '/mnt/c/Users'
    users = [user for user in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, user)) and user != 'desktop.ini']

    # Muestra y selecciona el usuario
    print("Por favor selecciona un usuario de Windows para la instalación:")
    for i, user in enumerate(users, start=1):
        print(f"{i}) {user}")

    while True:
        try:
            choice = int(input("Selecciona un usuario por número: "))
            if 1 <= choice <= len(users):
                return users[choice - 1]
            else:
                print("Selección inválida. Por favor, inténtalo de nuevo.")
        except ValueError:
            print("Por favor ingresa un número válido.")

def add_alias_to_bashrc(alias_name, command):
    bashrc_path = os.path.expanduser("~/.bashrc")
    alias_command = f"alias {alias_name}='{command}'\n"

    with open(bashrc_path, "a") as bashrc_file:
        bashrc_file.write(alias_command)

    print(f"Alias '{alias_name}' agregado a {bashrc_path}.")
    print(f"Usa '{alias_name}' para ejecutar el comando asociado.")

def main():
    install_venv()
    
    # Selecciona el usuario
    win_user = select_windows_user()
    install_dir = f"/mnt/c/Users/{win_user}/Documents/scrapper"
    
    # Elimina el contenido existente si el directorio no está vacío
    if os.path.exists(install_dir) and os.listdir(install_dir):
        print(f"El directorio {install_dir} no está vacío. Eliminando el contenido existente.")
        shutil.rmtree(install_dir)
    
    # Crea el directorio de instalación
    os.makedirs(install_dir, exist_ok=True)
    
    #
