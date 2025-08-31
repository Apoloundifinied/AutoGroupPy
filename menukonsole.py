import json
import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from main import main

console = Console()

CONFIG_FILE = "config.json"
COOKIES_FILE = "61579078355011.json"

# Config padrão
DEFAULT_CONFIG = {
    "grupos_por_conta": 1,
    "delay_entre_grupos": [20, 25],
    "delay_entre_contas": [20, 25],
    "usar_cookies": False
}

# Hotkeys
kb = KeyBindings()

@kb.add("p")
def _(event):
    console.print("[bold red]🚀 Iniciando script via atalho (p)...[/bold red]")
    iniciar_script()

def editar_cookies():
    console.print("[cyan]Abrindo arquivo de cookies pra edição...[/cyan]")
    if not os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            f.write("# Adicione seus cookies aqui\n")
    editor = os.getenv("EDITOR", "nano")
    subprocess.run([editor, COOKIES_FILE])

def editar_config():
    console.print("[cyan]Editando configuração do script...[/cyan]")

    # cria config se não existe
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    console.print("[bold yellow]Configurações atuais do script:[/bold yellow]")
    console.print_json(data=config)

    for key, valor in config.items():
        novo_valor = Prompt.ask(
            f"Novo valor para '{key}' (Enter = manter)",
            default=str(valor)
        )

        if novo_valor == str(valor):  # mantém valor
            continue

        try:
            # tenta interpretar como JSON (suporta int, float, bool, lista, etc.)
            config[key] = json.loads(novo_valor)
        except json.JSONDecodeError:
            config[key] = novo_valor  # mantém como string

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    console.print("[green]Configurações salvas![/green]")

def resetar_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    console.print("[bold green]Configurações resetadas para padrão![/bold green]")

def iniciar_script():
    try:
        main()
        console.print("[bold green]✅ Script finalizado com sucesso![/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao rodar script: {e}[/bold red]")

def menu():
    while True:
        console.print("\n[bold cyan]=== Painel Konsole ===[/bold cyan]")
        console.print("1 - Editar Cookies")
        console.print("2 - Editar Configurações")
        console.print("3 - Resetar Configuração")
        console.print("4 - Iniciar Script")
        console.print("q - Sair")

        escolha = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "4", "q"])

        if escolha == "1":
            editar_cookies()
        elif escolha == "2":
            editar_config()
        elif escolha == "3":
            resetar_config()
        elif escolha == "4":
            iniciar_script()
        elif escolha == "q":
            break

if __name__ == "__main__":
    console.print("[magenta]Dica: pressione [bold]P[/bold] a qualquer momento para rodar o script[/magenta]")
    menu()
