import os

def carregar_contas(path="contas.txt", cookies_dir="cookies"):
    contas = []
    bloco = {}

    with open(path, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()

            # Linha vazia → salva bloco e começa outro
            if not linha:
                if bloco:
                    # Se tiver c_user ou login, define caminho do cookie
                    c_user = bloco.get("c_user") or bloco.get("login")
                    if c_user:
                        bloco["cookie_file"] = os.path.join(cookies_dir, f"{c_user}.json")
                    contas.append(bloco)
                    bloco = {}
                continue

            # Parse chave:valor
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                bloco[chave.strip().lower()] = valor.strip()

        # Adiciona último bloco
        if bloco:
            c_user = bloco.get("c_user") or bloco.get("login")
            if c_user:
                bloco["cookie_file"] = os.path.join(cookies_dir, f"{c_user}.json")
            contas.append(bloco)

    return contas
