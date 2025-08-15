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

    # Campo Nome do Grupo (captura se estiver em PT ou EN)
    nome_input = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//input[@type='text' and (contains(@aria-label,'roup') or contains(@placeholder,'roup'))]"
        ))
    )
    nome_input.clear()
    nome_input.send_keys(nome)

    # Botão para abrir opções de privacidade
    privacidade_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(@aria-label,'rivacy') or contains(@aria-label,'rivacidade')]"
        ))
    )
    privacidade_btn.click()

    # Selecionar "Público"
    publico_option = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//span[contains(text(),'Public')] | //span[contains(text(),'Público')]"
        ))
    )
    publico_option.click()

    # Botão Criar
    criar_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='button' and (contains(@aria-label,'Create') or contains(@aria-label,'Criar'))]"
        ))
    )
    criar_btn.click()

    # Esperar carregar a página do grupo criado
    WebDriverWait(driver, 30).until(EC.url_contains("facebook.com/groups"))
    group_url = driver.current_url
    group_id = group_url.split("/")[-2]
    return group_id, group_url

def adicionar_foto(driver, path_img):
    try:
        driver.get(driver.current_url + "/about")
        time.sleep(3)
        botao_foto = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Edit group photo' or @aria-label='Editar foto do grupo']"))
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
        campo = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )
        campo.click()
        campo.send_keys(msg)
        time.sleep(1)
        campo.send_keys(u'\ue007')
        time.sleep(2)
    except Exception as e:
        logging.warning(f"[POST] Falha ao postar mensagem: {e}")

# === INÍCIO ===
with open(NOMES_FILE) as f:
    nomes = [x.strip() for x in f.readlines()]
with open(MENSAGEM_FILE) as f:
    mensagem = f.read()
fotos = list(FOTOS_DIR.glob("*.jpg"))

driver = uc.Chrome(headless=False)

try:
    carregar_cookies(driver, COOKIE_FILE)

    for _ in range(CONFIG["grupos_por_conta"]):
        nome_grupo = random.choice(nomes)
        try:
            group_id, group_url = criar_grupo(driver, nome_grupo)
            adicionar_foto(driver, random.choice(fotos))
            postar_mensagem(driver, mensagem)
            logging.info(f"[SUCESSO] Grupo: {nome_grupo} | {group_url}")
            print(f"[✔] Grupo criado: {nome_grupo}")

        except (InvalidSessionIdException, TimeoutException) as e:
            logging.error(f"[ERRO] {nome_grupo} | Sessão perdida: {e}")
            print(f"[X] Sessão perdida ao criar grupo: {e}")
            break  # para o loop se o navegador fechar

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
