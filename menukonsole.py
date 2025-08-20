import json
import os
from rich.console import Console
from rich.prompt import Prompt
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from main import main 

console = Console()

CONFIG_FILE = "config.json"
COOKIES_FILE = "61579078355011.json"

# Hotkeys
kb = KeyBindings()

@kb.add("p")
def _(event):
    console.print("[bold red]🚀 Script iniciado via atalho![/bold red]")

def editar_cookies():
    console.print("[cyan]Abrindo arquivo de cookies pra edição...[/cyan]")
    if not os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "w") as f:
            f.write("# Adicione seus cookies aqui\n")
    os.system(f"{os.getenv('EDITOR','nano')} {COOKIES_FILE}")

def editar_config():
    console.print("[cyan]Editando configuração do script...[/cyan]")
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "grupos_por_conta": 1,
            "delay_entre_grupos": [20, 25],
            "delay_entre_contas": [20, 25],
            "usar_cookies": False
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    console.print("[bold yellow]Configurações atuais do script:[/bold yellow]")
    console.print_json(data=config)

    for key in config:
        novo_valor = Prompt.ask(f"Novo valor para '{key}' (Enter = manter)", default=str(config[key]))
        try:
            config[key] = eval(novo_valor)  
        except:
            config[key] = novo_valor

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    console.print("[green]Configurações salvas![/green]")
def iniciar_script():
    main()
    console.print("[bold red]🚀 Script iniciado![/bold red]")

def menu():
    while True:
        console.print("\n[bold cyan]=== Painel Konsole ===[/bold cyan]")
        console.print("1 - Editar Cookies")
        console.print("2 - Editar Configurações")
        console.print("3 - Iniciar Script")
        console.print("q - Sair")

        escolha = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "q"])
        
        if escolha == "1":
            editar_cookies()
        elif escolha == "2":
            editar_config()
        elif escolha == "3":
            iniciar_script()
        elif escolha == "q":
            break

if __name__ == "__main__":
    console.print("[magenta]Dica: Pressione Ctrl+Enter para iniciar o script a qualquer momento[/magenta]")
    prompt("Pressione Enter para abrir o menu...\n", key_bindings=kb)
    menu()
