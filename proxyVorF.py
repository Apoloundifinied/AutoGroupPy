import json
import requests
from requests.exceptions import RequestException, ProxyError, ConnectTimeout


PROXY_FILE = "packge.json"


TEST_URL = "https://httpbin.org/ip"

def load_proxies(filename):
    with open(filename, "r") as f:
        proxies = json.load(f)
    return proxies

def test_proxy(ip, port, timeout=5):
    proxy_str = f"http://{ip}:{port}"
    proxies = {
        "http": proxy_str,
        "https": proxy_str
    }
    try:
        response = requests.get(TEST_URL, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            return True
    except (ProxyError, ConnectTimeout, RequestException):
        pass
    return False

def main():
    proxies = load_proxies(PROXY_FILE)
    print(f"Testando {len(proxies)} proxies...\n")

    for proxy in proxies:
        ip = proxy.get("ip")
        port = proxy.get("port")
        if not ip or not port:
            print(f"Proxy inválido (faltando ip ou port): {proxy}")
            continue

        funcionando = test_proxy(ip, port)
        status = "Funcionando ✅" if funcionando else "Não funciona ❌"
        print(f"{ip}:{port} -> {status}")""

if __name__ == "__main__":
    main()
