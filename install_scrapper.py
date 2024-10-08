import os
import subprocess
import sys
import shutil

def install_venv():
    # Actualiza los repositorios de paquetes
    subprocess.run(['sudo', 'apt', 'update'], check=True)
    
    # Instala python3.10-venv directamente
    try:
        print("Instalando python3.10-venv...")
        subprocess.run(['sudo', 'apt', 'install', '-y', 'python3.10-venv'], check=True)
    except subprocess.CalledProcessError:
        print("Error: No se pudo instalar python3.10-venv.")
        sys.exit(1)

    # Verifica si ensurepip está disponible
    try:
        subprocess.run(['python3.10', '-m', 'ensurepip', '--help'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("ensurepip no está disponible. Intentando instalarlo o verificar pip...")
        
        # Prueba instalar python3-pip, pero maneja el error si no está disponible
        try:
            subprocess.run(['sudo', 'apt', 'install', '-y', 'python3-pip'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: No se pudo instalar python3-pip. {e}")
            print("Es posible que el paquete ya no esté disponible. Intentando continuar con pip...")
        
        # Verifica si pip está instalado de alguna forma
        try:
            subprocess.run(['pip3', '--version'], check=True)
        except subprocess.CalledProcessError:
            print("pip no está disponible. No se puede continuar.")
            sys.exit(1)


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
    
    # Navega al directorio de instalación
    os.chdir(install_dir)
    
    # Clona el repositorio
    subprocess.run(['git', 'clone', 'https://github.com/nildiert/checho.git', '.'], check=True)
    
    # Crea un entorno virtual en el directorio de instalación
    try:
        subprocess.run(['python3', '-m', 'venv', '.venv'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al crear el entorno virtual: {e}")
        sys.exit(1)
    
    # Activa el entorno virtual e instala las dependencias
    activate_script = os.path.join(install_dir, '.venv/bin/activate')
    subprocess.run([f"bash -c 'source {activate_script} && pip install --upgrade pip && pip install -r requirements.txt'"], shell=True, check=True)
    
    # Asegúrate de que el script principal sea ejecutable
    subprocess.run(['chmod', '+x', 'main.py'], check=True)
    
    # Agrega los alias al archivo de configuración de bash
    add_alias_to_bashrc("activate_scrapper", f"cd {install_dir} && source .venv/bin/activate")
    add_alias_to_bashrc("scrapper", "python3 main.py")
    
    # Ejecuta source ~/.bashrc para que los aliases queden disponibles de inmediato
    bash_command = "source ~/.bashrc"
    subprocess.run(bash_command, shell=True, executable='/bin/bash')

    print(f"Instalación completa. El repositorio está instalado en {install_dir}.")
    print(f"Para activar el entorno virtual, ejecuta 'activate_scrapper'.")

if __name__ == "__main__":
    main()
