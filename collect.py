import requests
import re

# Список источников (включая твой приоритетный источник)
URLS = [
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt", # Самый надежный
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass/bypass-all.txt",
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass-unsecure/bypass-unsecure-all.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vless_ru.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-all.txt"
]

def main():
    unique_configs = set()
    
    for url in URLS:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # 1. Ищем только VLESS
                found_vless = re.findall(r'vless://[^\s#]+(?:#[^\s]*)?', response.text)
                
                for cfg in found_vless:
                    # 2. Фильтруем: оставляем только Reality (security=reality)
                    # Выкидываем VMess, Trojan, SS и обычный TLS
                    if "security=reality" in cfg:
                        unique_configs.add(cfg.strip())
                
                print(f"Обработано: {url}")
            else:
                print(f"Ошибка {response.status_code}: {url}")
        except Exception as e:
            print(f"Ошибка связи с {url}: {e}")

    # Сохраняем результат
    if unique_configs:
        with open("all_configs.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(list(unique_configs))))
        print(f"\nГотово! Собрано {len(unique_configs)} Reality-конфигов.")
    else:
        print("\nРабочих конфигов Reality не найдено!")

if __name__ == "__main__":
    main()
