import requests
import re

# Список ваших источников (все RAW ссылки)
URLS = [
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
            # Имитируем браузер, чтобы GitHub не блокировал частые запросы
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Находим все ссылки vless, vmess, trojan, ss
                configs = re.findall(r'(vless://[^\s#]+|vmess://[^\s#]+|trojan://[^\s#]+|ss://[^\s#]+)', response.text)
                for cfg in configs:
                    # Очищаем от мусора и добавляем в набор (авто-удаление дублей)
                    unique_configs.add(cfg.strip())
                print(f"Успешно: {url} (найдено {len(configs)})")
            else:
                print(f"Ошибка {response.status_code}: {url}")
        except Exception as e:
            print(f"Ошибка запроса {url}: {e}")

    # Сохраняем в один файл
    if unique_configs:
        with open("all_configs.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(list(unique_configs))))
        print(f"\nИТОГО: Собрано {len(unique_configs)} уникальных подписей.")
    else:
        print("\nКонфиги не найдены!")

if __name__ == "__main__":
    main()
