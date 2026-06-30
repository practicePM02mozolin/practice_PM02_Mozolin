import requests
import time
import math
import tracemalloc
from datetime import datetime

# Глобальный кеш ответов API - потенциальная утечка памяти
API_CACHE = {}

def fetch_exchange_rate(currency_from, currency_to):
    """
    Получение курса валют с публичного API.
    Ошибка 1: Нет обработки таймаутов
    Ошибка 2: Кеш без expiration (утечка)
    """
    cache_key = f"{currency_from}_{currency_to}"
    
    # Проверка кеша
    if cache_key in API_CACHE:
        return API_CACHE[cache_key]
    
    # Имитация запроса к API (в реальности здесь был бы requests.get)
    # Для демонстрации используем заглушку с задержкой
    time.sleep(0.5)
    
    # Ошибка 3: Неверное преобразование типов (строка вместо float)
    # В реальном API пришел бы JSON, но мы имитируем ошибку
    mock_response = {
        "base": currency_from,
        "target": currency_to,
        "rate": "85.43",  # Строка, а не число!
        "timestamp": int(time.time())
    }
    
    # Ошибка 4: KeyError в JSON ответе - обращение по несуществующему ключу
    rate_value = mock_response["rates"]  # Такого ключа нет!
    
    # Кешируем результат (без проверки размера - утечка)
    API_CACHE[cache_key] = rate_value
    return rate_value

def convert_currency(amount, from_currency, to_currency):
    """Конвертация валюты с логической ошибкой"""
    rate = fetch_exchange_rate(from_currency, to_currency)
    
    # Ошибка: неверное преобразование типов
    # rate - строка, но мы пытаемся умножить float на str
    result = amount * rate  # TypeError!
    
    return result

def process_currency_data(transactions):
    """Обработка списка транзакций"""
    results = []
    
    for tx in transactions:
        # Ошибка: нет обработки отсутствующих ключей
        amount = tx["amount"]  # KeyError, если ключа нет
        from_currency = tx["from"]
        to_currency = tx["to"]
        
        try:
            converted = convert_currency(amount, from_currency, to_currency)
            results.append({
                "original": tx,
                "converted": converted,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            results.append({
                "original": tx,
                "error": str(e)
            })
    
    return results

if __name__ == "__main__":
    # Включаем tracemalloc для отслеживания памяти
    tracemalloc.start()
    
    # Тестовые данные с ошибками
    test_transactions = [
        {"amount": 100.0, "from": "USD", "to": "EUR"},
        {"amount": 250.0, "from": "EUR", "to": "GBP"},
        {"amount": 50.0},  # Ошибка: нет ключей 'from' и 'to'
        {"amount": 1000.0, "from": "USD", "to": "JPY"},
    ]
    
    print("Начинаем обработку транзакций...")
    result = process_currency_data(test_transactions)
    
    print("\nРезультаты обработки:")
    for item in result:
        print(item)
    
    snapshot = tracemalloc.take_snapshot()
    print("\nТоп-5 строк по потреблению памяти:")
    for stat in snapshot.statistics('lineno')[:5]:
        print(stat)
