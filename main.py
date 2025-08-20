import time
import json
import random
import logging
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException, TimeoutException

# === CONFIGURAÇÕES ===
CONFIG = json.load(open("config.json"))

if "delay_entre_grupsos" not in CONFIG:
    CONFIG["delay_entre_grupsos"] = [2, 5]

logging.basicConfig(filename="logs/grupos.log", level=logging.INFO)

COOKIE_FILE = "cookies/61579078355011.json"
NOMES_FILE = "nomes.txt"
MENSAGEM_FILE = "mensagem.txt"
FOTOS_DIR = Path("fotos")


def delay(seg_min_max):
    t = random.randint(*seg_min_max)
    time.sleep(t)


def carregar_cookies(driver, cookie_file):
    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    driver.get("https://facebook.com")
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    WebDriverWait(driver, 15).until(EC.url_contains("facebook.com"))


def criar_grupo(driver, nome):
    driver.get("https://www.facebook.com/groups/create/")

    # DEBUG: salvar HTML da página
    with open("debug_input.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("[DEBUG] Página salva em debug_input.html")

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

    # Selecionar Privacidade (robusto)
    try:
        textos_privacidade = ["Public", "Público", "Friends", "Only me"]
        priv_selecionado = False

        for texto in textos_privacidade:
            try:
                priv_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[text()='{texto}']/.."))
                )
                priv_btn.click()
                print(f"[✔] Privacidade definida: {texto}")
                priv_selecionado = True
                break
            except TimeoutException:
                continue

        if not priv_selecionado:
            print("[!] Botão de privacidade não encontrado, pulando.")

    except Exception as e:
        print(f"[!] Não conseguiu selecionar privacidade: {e}")

    # Botão Criar
    criar_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='button' and (contains(@aria-label,'Create') or contains(@aria-label,'Criar'))]"
        ))
    )
    criar_btn.click()
    print("[✔] Botão Criar clicado.")

    # Esperar carregar a página do grupo criado
    try:
        WebDriverWait(driver, 15).until(EC.url_contains("facebook.com/groups"))
        group_url = driver.current_url
        group_id = group_url.split("/")[-2]
    except TimeoutException:
        group_url = driver.current_url
        group_id = None
        print("[!] Não foi possível capturar ID do grupo.")

    return group_id, group_url


def adicionar_foto(driver, path_img):
    try:
        
        driver.get(driver.current_url + "/about")
        time.sleep(3)
        botao_foto = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@aria-label='Edit group photo' or @aria-label='Editar foto do grupo']"
            ))
        )
        botao_foto.click()
        time.sleep(2)
        enviar = driver.find_element(By.XPATH, "//input[@type='file']")
        enviar.send_keys(str(path_img.resolve()))
        time.sleep(5)
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
        campo.send_keys(u'\ue007')
        time.sleep(2)
    except Exception as e:
        logging.warning(f"[POST] Falha ao postar mensagem: {e}")


def main():
    with open(NOMES_FILE) as f:
        nomes = [x.strip() for x in f.readlines() if x.strip()]

    with open(MENSAGEM_FILE) as f:
        mensagem = f.read().strip()

    fotos = list(FOTOS_DIR.glob("*.jpg"))

    if not nomes:
        print("[X] Arquivo de nomes vazio.")
    if not fotos:
        print("[X] Pasta de fotos vazia.")

    driver = uc.Chrome(headless=False)

    try:
        carregar_cookies(driver, COOKIE_FILE)

        for _ in range(CONFIG.get("grupos_por_conta", 1)):
            if not nomes:
                break
            nome_grupo = random.choice(nomes)
            try:
                group_id, group_url = criar_grupo(driver, nome_grupo)
                if fotos:
                    adicionar_foto(driver, random.choice(fotos))
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
                logging.error(f"[ERRO] {nome_grupo} | {e} | Screenshot: {screenshot_path}")
                print(f"[X] Falha ao criar grupo: {e}. Screenshot salva em {screenshot_path}")

            delay(CONFIG["delay_entre_grupsos"])

    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()
