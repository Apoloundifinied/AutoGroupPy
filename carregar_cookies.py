import json
from pathlib import Path

def carregar_cookies(driver, email):
    """Carrega cookies do arquivo JSON referente ao email"""
    cookie_file = Path("cookies") / f"{email}.json"
    if not cookie_file.exists():
        raise FileNotFoundError(f"Arquivo de cookies não encontrado: {cookie_file}")

    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    for cookie in cookies:
        # O domínio precisa ser .facebook.com para funcionar em todas as páginas
        if "facebook" in cookie.get("domain", ""):
            driver.add_cookie(cookie)
