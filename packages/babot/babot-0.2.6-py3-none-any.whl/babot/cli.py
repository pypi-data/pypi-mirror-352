import os
import shutil
import subprocess
import sys
from babot import __version__

# Rutas globales
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template")
MAIN_SCRIPT = os.path.join(os.getcwd(), "main.py")

DEFAULT_AGENT = "babot"  # Nombre del agente base funcional

def init_project(nombre_proyecto):
    """Inicializa un nuevo proyecto con la estructura base."""
    if os.path.exists(nombre_proyecto):
        print(f"El directorio '{nombre_proyecto}' ya existe. Por favor, elige otro nombre.")
        return

    try:
        # Copiar la plantilla al nuevo directorio
        shutil.copytree(TEMPLATE_PATH, nombre_proyecto)
        # shutil.copy(os.path.join(nombre_proyecto, ".env.example"), os.path.join(nombre_proyecto, ".env"))
        print(f"Proyecto '{nombre_proyecto}' creado exitosamente.")
        print("Estructura inicial generada. Instala las dependencias con:")
        print(f"\n  cd {nombre_proyecto} && pip install -r requirements.txt")
        print("\nEjecuta el agente Babot con:")
        print(f"\n  babot run")
    except Exception as e:
        print(f"Error al crear el proyecto: {e}")

def create_agent(nombre_agente):
    """Crea un nuevo agente basado en el agente 'babot'."""
    agentes_dir = "agentes"
    config_dir = "config"

    if not os.path.exists(agentes_dir) or not os.path.exists(config_dir):
        print("Parece que no estás dentro de un proyecto válido. Usa 'babot init' primero.")
        return

    archivo_py = os.path.join(agentes_dir, f"{nombre_agente}.py")
    archivo_yaml = os.path.join(config_dir, f"{nombre_agente}.yaml")

    if os.path.exists(archivo_py) or os.path.exists(archivo_yaml):
        print(f"El agente '{nombre_agente}' ya existe.")
        return

    try:
        # Copiar archivo base de código y configuración
        shutil.copy(os.path.join(agentes_dir, f"{DEFAULT_AGENT}.py"), archivo_py)
        shutil.copy(os.path.join(config_dir, f"{DEFAULT_AGENT}.yaml"), archivo_yaml)
        print(f"Agente '{nombre_agente}' creado exitosamente basado en '{DEFAULT_AGENT}'.")
    except Exception as e:
        print(f"Error al crear el agente: {e}")

def run_agent(nombre_agente):
    """Ejecuta un agente existente en una nueva ventana."""
    archivo_py = os.path.join("agentes", f"{nombre_agente}.py")
    if not os.path.exists(archivo_py):
        print(f"El agente '{nombre_agente}' no existe.")
        return

    try:
        # Ejecutar en una nueva ventana
        if os.name == "nt":  # Windows
            subprocess.Popen(["start", "python", archivo_py], shell=True)
        else:  # Linux/Mac
            subprocess.Popen(["x-terminal-emulator", "-e", f"python {archivo_py}"])
        print(f"Ejecutando agente '{nombre_agente}' en una nueva ventana.")
    except Exception as e:
        print(f"Error al ejecutar el agente: {e}")

def run_menu():
    """Ejecuta el menú principal (main.py)."""
    if not os.path.exists(MAIN_SCRIPT):
        print("El archivo main.py no fue encontrado. Verifica la instalación.")
        return

    try:
        subprocess.run([sys.executable, MAIN_SCRIPT])
    except Exception as e:
        print(f"Error al ejecutar el menú principal: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Babot CLI")
    parser.add_argument("--version", action="version", version=f"Babot {__version__}")


    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando init
    parser_init = subparsers.add_parser("init", help="Inicializa un nuevo proyecto")
    parser_init.add_argument("nombre_proyecto", help="Nombre del proyecto")

    # Comando create
    parser_create = subparsers.add_parser("create", help="Crea un nuevo agente")
    parser_create.add_argument("nombre_agente", help="Nombre del agente")

    # Comando run
    parser_run = subparsers.add_parser("run", help="Ejecuta un agente o abre el menú principal")
    parser_run.add_argument("nombre_agente", nargs="?", default=None, help="Nombre del agente (opcional)")

    args = parser.parse_args()

    if args.command == "init":
        init_project(args.nombre_proyecto)
    elif args.command == "create":
        create_agent(args.nombre_agente)
    elif args.command == "run":
        if args.nombre_agente:
            run_agent(args.nombre_agente)
        else:
            run_menu()
    else:
        parser.print_help()

