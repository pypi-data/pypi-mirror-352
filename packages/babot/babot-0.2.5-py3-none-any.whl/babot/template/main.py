import os
import subprocess
import sys
from ui import show_menu, show_agents, prompt_input, show_message

AGENTS_DIR = "agentes"
CONFIG_DIR = "config"
CONFIG_BASE = "config_base.py"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template")


def init_project(nombre_proyecto):
    """Inicializa un nuevo proyecto con la estructura base."""
    if os.path.exists(nombre_proyecto):
        show_message(f"El directorio '{nombre_proyecto}' ya existe. Por favor, elige otro nombre.", "red")
        return
    try:
        shutil.copytree(TEMPLATE_PATH, nombre_proyecto)
        shutil.copy(os.path.join(nombre_proyecto, ".env.example"), os.path.join(nombre_proyecto, ".env"))
        show_message(f"Proyecto '{nombre_proyecto}' creado exitosamente.")
    except Exception as e:
        show_message(f"Error al crear el proyecto: {e}", "red")


def list_agents():
    """Lista los agentes disponibles."""
    if not os.path.exists(AGENTS_DIR):
        os.makedirs(AGENTS_DIR)
    return [f.replace(".py", "") for f in os.listdir(AGENTS_DIR) if f.endswith(".py")]


def run_agent():
    """Muestra agentes disponibles y permite ejecutarlos o modificarlos."""
    agents = list_agents()
    if not agents:
        show_message("No hay agentes disponibles para ejecutar.", "red")
        return
    show_agents(agents)

    choice = prompt_input("Selecciona un agente para ejecutar o modificar")
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(agents):
        show_message("Selección inválida.", "red")
        return

    agent_name = agents[int(choice) - 1] 
    action = prompt_input(f"¿Qué deseas hacer con '{agent_name}'? (1: Ejecutar, 2: Modificar configuración)") [cite: 5]
    if action == "1":
        agent_path = os.path.join(AGENTS_DIR, f"{agent_name}.py")

        # Obtén la ruta al intérprete de Python del entorno virtual actual
        python_executable = sys.executable 

        try:
            subprocess.run([python_executable, agent_path])
        except Exception as e:
            show_message(f"Error al ejecutar el agente: {e}", "red")
    elif action == "2":
        modify_agent_config(agent_name)


def create_agent():
    """Crea un nuevo agente."""
    nombre_agente = prompt_input("Nombre del nuevo agente")
    agentes_dir = AGENTS_DIR
    config_dir = CONFIG_DIR

    archivo_py = os.path.join(agentes_dir, f"{nombre_agente}.py")
    archivo_yaml = os.path.join(config_dir, f"{nombre_agente}.yaml")

    if os.path.exists(archivo_py) or os.path.exists(archivo_yaml):
        show_message(f"El agente '{nombre_agente}' ya existe.", "red")
        return

    try:
        # Genera el archivo .py y su configuración
        with open(archivo_py, "w") as py_file:
            py_file.write(f"# Agente {nombre_agente.capitalize()} generado automáticamente\n")
        with open(archivo_yaml, "w") as yaml_file:
            yaml_file.write(f"# Configuración para {nombre_agente}\n")
        show_message(f"Agente '{nombre_agente}' creado exitosamente.")
    except Exception as e:
        show_message(f"Error al crear el agente: {e}", "red")


def modify_agent_config(agent_name=None):
    """Modifica la configuración de un agente existente."""
    if not agent_name:
        agents = list_agents()
        if not agents:
            show_message("No hay agentes disponibles para modificar.", "red")
            return
        show_agents(agents)
        choice = prompt_input("Selecciona un agente para modificar")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(agents):
            show_message("Selección inválida.", "red")
            return
        agent_name = agents[int(choice) - 1]

    config_path = os.path.join(CONFIG_DIR, f"{agent_name}.yaml")
    if not os.path.exists(config_path):
        show_message(f"La configuración del agente '{agent_name}' no existe.", "red")
        return

    os.system(f"notepad {config_path}" if os.name == "nt" else f"nano {config_path}")
    show_message(f"Configuración de '{agent_name}' modificada.")


def configure_general_settings():
    """Modifica configuraciones generales."""
    os.system(f"notepad {CONFIG_BASE}" if os.name == "nt" else f"nano {CONFIG_BASE}")
    show_message("Configuraciones generales actualizadas.")


if __name__ == "__main__":
    while True:
        choice = show_menu()
        if choice == "1":
            run_agent()
        elif choice == "2":
            modify_agent_config()
        elif choice == "3":
            create_agent()
        elif choice == "4":
            configure_general_settings()
        elif choice == "0":
            show_message("Saliendo del programa. ¡Hasta pronto!", "yellow")
            break
