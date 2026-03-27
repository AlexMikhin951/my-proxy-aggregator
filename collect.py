import requests
import re
import asyncio
import random

# Настройки
LIMIT = 999
TIMEOUT = 2.0  # Секунд на проверку одного сервера
CONCURRENCY = 100 # Сколько серверов проверять одновременно

SOURCES = [
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt", # ПРИОРИТЕТ
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass/bypass-all.txt",
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass-unsecure/bypass-unsecure-all.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vless_ru.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-all.txt"
]

async def check_port(host, port):
    """Быстрая проверка доступности TCP порта."""
    try:
        # Пытаемся открыть соединение
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=TIMEOUT)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def validate_configs(configs):
    """Проверка списка конфигов в несколько потоков."""
    valid_configs = []
    # Ограничиваем количество одновременных подключений
    sem = asyncio.Semaphore(CONCURRENCY)

    async def task(cfg):
        async with sem:
            # Регулярка для извлечения хоста и порта
            match = re.search(r'@([^:/]+):(\d+)', cfg)
            if match:
                host, port = match.group(1), int(match.group(2))
                if await check_port(host, port):
                    valid_configs.append(cfg)

    await asyncio.gather(*(task(cfg) for cfg in configs))
    return valid_configs

def fetch_all():
    """Сбор сырых данных из всех источников."""
    all_raw = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in SOURCES:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                # Ищем только vless ссылки
                found = re.findall(r'vless://[^\s#]+(?:#[^\s]*)?', res.text)
                # Фильтруем только Reality
                for c in found:
                    clean_c = c.strip()
                    if "security=reality" in clean_c:
                        all_raw.append(clean_c)
                print(f"Загружено: {url}")
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")
    return all_raw

def deduplicate(configs):
    """Удаление дубликатов по адресу сервера (IP:Port)."""
    unique = []
    seen_nodes = set()
    for cfg in configs:
        # Выделяем часть с IP и портом
        node_match = re.search(r'@([^:/]+:\d+)', cfg)
        if node_match:
            node = node_match.group(1)
            if node not in seen_nodes:
                seen_nodes.add(node)
                unique.append(cfg)
    return unique

async def main():
    print("--- Запуск агрегатора ---")
    
    # 1. Собираем всё
    raw_configs = fetch_all()
    if not raw_configs:
        print("Конфиги не найдены. Выход.")
        return

    # 2. Удаляем дубликаты
    unique_configs = deduplicate(raw_configs)
    print(f"Уникальных Reality-серверов после очистки: {len(unique_configs)}")

    # 3. Перемешиваем, чтобы список обновлялся
    random.shuffle(unique_configs)

    # 4. Проверяем порты
    print(f"Начинаю проверку портов (в {CONCURRENCY} потоков)...")
    valid_list = await validate_configs(unique_configs)
    print(f"Проверку прошли (порт открыт): {len(valid_list)}")

    # 5. Берем лучшие (до лимита)
    final_list = valid_list[:LIMIT]

    # 6. Записываем в файл
    with open("all_configs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_list))
    
    print(f"--- Готово! Файл all_configs.txt содержит {len(final_list)} рабочих строк ---")

if __name__ == "__main__":
    asyncio.run(main())
