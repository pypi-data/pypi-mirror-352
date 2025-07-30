from rich.console import Console
from rich.table import Table

console = Console()

def show_menu():
    """Muestra el menú principal y devuelve la elección del usuario."""
    console.rule("[bold blue]Babot - Menú Principal[/bold blue]")
    options = [
        "1. Correr agente",
        "2. Modificar configuración del agente",
        "3. Crear agente",
        "4. Clonar agente",
        "5. Configuraciones generales",
        "0. Salir",
    ]
    for option in options:
        console.print(option)
    choice = input("\nSelecciona una opción: ")
    return choice

def show_agents(agents):
    """Muestra una lista de agentes disponibles."""
    table = Table(title="Agentes disponibles")
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Nombre", justify="left", style="white")
    for i, agent in enumerate(agents, start=1):
        table.add_row(str(i), agent)
    console.print(table)

def prompt_input(prompt):
    """Solicita una entrada del usuario."""
    return input(f"{prompt}: ")

def show_message(message, style="green"):
    """Muestra un mensaje en la consola."""
    console.print(f"[{style}]{message}[/{style}]")
