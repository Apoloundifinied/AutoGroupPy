import time
import json
import random
import logging
import traceback
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, TimeoutException

# === CONFIGURAÇÕES ===
CONFIG = json.load(open("config.json", encoding="utf-8"))

if "delay_entre_grupos" not in CONFIG:
    CONFIG["delay_entre_grupos"] = [2, 5]

logging.basicConfig(
    filename="logs/grupos.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

COOKIE_FILE = "cookies/61579078355011.json"
NOMES_FILE = "nomes.txt"
MENSAGEM_FILE = "mensagem.txt"

# Foto padrão
FOTO_PADRAO = Path(r"C:\Users\yamii\AutoGroupPy\fotos\group.jpg")


def delay(seg_min_max):
    t = random.uniform(*seg_min_max)  # mais natural que randint
    time.sleep(t)


def iniciar_driver(headless=False):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    if headless:
        options.add_argument("--headless=new")
    return uc.Chrome(options=options)


def carregar_cookies(driver, cookie_file):
    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    driver.get("https://facebook.com")
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get("https://facebook.com")
    WebDriverWait(driver, 15).until(EC.url_contains("facebook.com"))


def criar_grupo(driver, nome):
    driver.get("https://www.facebook.com/groups/create/")

    # Campo Nome do Grupo
    try:
        nome_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//input[@type='text' and (contains(@aria-label,'Nome') or contains(@aria-label,'Name'))]"
            ))
        )
        print("[✔] Campo do nome encontrado por label.")
    except TimeoutException:
        print("[!] Não achou pelo label, tentando fallback...")
        nome_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@type='text'])[1]"))
        )
        print("[✔] Campo do nome encontrado pelo fallback.")

    nome_input.clear()
    nome_input.send_keys(nome)
    print(f"[✔] Nome do grupo preenchido: {nome}")

    # Botão Criar
    criar_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='button' and (contains(.,'Criar') or contains(.,'Create'))]"
        ))
    )
    criar_btn.click()
    print("[✔] Botão Criar clicado.")

    # Esperar carregar a página do grupo criado
    try:
        WebDriverWait(driver, 20).until(EC.url_contains("facebook.com/groups/"))
        group_url = driver.current_url
        if "/about" in group_url or "/create" in group_url:
            group_url = group_url.split("?")[0].replace("/about", "").replace("/create", "")
            driver.get(group_url)

        # Corrigir caso caia em /about ou /create
        if "/about" in group_url or "/create" in group_url:
            group_url = group_url.split("?")[0].replace("/about", "").replace("/create", "")
            driver.get(group_url)

        group_id = group_url.split("/")[-2]
        print(f"✅ Grupo criado: {group_url}")
    except TimeoutException:
        group_url = driver.current_url
        group_id = None
        print("[!] Não foi possível capturar ID do grupo.")

    return group_id, group_url


def adicionar_foto(driver, path_img):
    try:
        driver.get(driver.current_url + "/about")
        botao_foto = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@aria-label='Edit group photo' or @aria-label='Editar foto do grupo']"
            ))
        )
        botao_foto.click()
        enviar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        enviar.send_keys(str(path_img.resolve()))
        WebDriverWait(driver, 20).until_not(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        print("[✔] Foto adicionada ao grupo.")
    except Exception as e:
        logging.warning(f"[IMG] Falha ao adicionar imagem: {e}")


def postar_mensagem(driver, msg):
    try:
        campo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )
        campo.click()
        campo.send_keys(msg)
        time.sleep(1)
        campo.send_keys(u'\ue007')  # Enter
        print("[✔] Mensagem postada.")
        time.sleep(2)
    except Exception as e:
        logging.warning(f"[POST] Falha ao postar mensagem: {e}")


def main():
    if not Path(NOMES_FILE).exists():
        print("[X] Arquivo de nomes não encontrado.")
        return
    if not Path(MENSAGEM_FILE).exists():
        print("[X] Arquivo de mensagem não encontrado.")
        return
    if not Path(COOKIE_FILE).exists():
        print("[X] Arquivo de cookies não encontrado.")
        return

    with open(NOMES_FILE, encoding="utf-8") as f:
        nomes = [x.strip() for x in f.readlines() if x.strip()]

    with open(MENSAGEM_FILE, encoding="utf-8") as f:
        mensagem = f.read().strip()

    driver = iniciar_driver(headless=False)

    try:
        carregar_cookies(driver, COOKIE_FILE)

        for _ in range(CONFIG.get("grupos_por_conta", 1)):
            if not nomes:
                break
            nome_grupo = random.choice(nomes)
            try:
                group_id, group_url = criar_grupo(driver, nome_grupo)

                if FOTO_PADRAO.exists():
                    adicionar_foto(driver, FOTO_PADRAO)
                else:
                    logging.warning("[IMG] Foto padrão não encontrada, criando sem imagem.")

                postar_mensagem(driver, mensagem)
                logging.info(f"[SUCESSO] Grupo: {nome_grupo} | {group_url}")
                print(f"[✔] Grupo criado: {nome_grupo} -> {group_url}")

            except (InvalidSessionIdException, TimeoutException) as e:
                logging.error(f"[ERRO] {nome_grupo} | Sessão perdida: {e}")
                print(f"[X] Sessão perdida ao criar grupo: {e}")
                break

            except Exception as e:
                timestamp = int(time.time())
                screenshot_path = f'erro_criar_grupo_{timestamp}.png'
                try:
                    driver.save_screenshot(screenshot_path)
                except InvalidSessionIdException:
                    screenshot_path = None
                logging.error(f"[ERRO] {nome_grupo} | {e}\n{traceback.format_exc()}")
                print(f"[X] Falha ao criar grupo: {e}. Screenshot salva em {screenshot_path}")

            delay(CONFIG["delay_entre_grupos"])

    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()
