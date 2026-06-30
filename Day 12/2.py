import requests
import time
import math
import tracemalloc
from datetime import datetime
from collections import OrderedDict

# Глобальный кеш ответов API - потенциальная утечка памяти
API_CACHE = {}

def fetch_exchange_rate(currency_from, currency_to):
    """
    Получение курса валют с публичного API.
    """
    cache_key = f"{currency_from}_{currency_to}"
    
    # Проверка кеша
    if cache_key in API_CACHE:
        return API_CACHE[cache_key]
    
    # Имитация запроса к API
    time.sleep(0.5)
    
    # ============ breakpoint() №1: Перед созданием ответа ============
    breakpoint()  # Точка остановки 1 - проверка входных параметров
    
    mock_response = {
        "base": currency_from,
        "target": currency_to,
        "rate": "85.43",  # Строка, а не число!
        "timestamp": int(time.time())
    }
    
    # ============ breakpoint() №2: После создания ответа ============
    breakpoint()  # Точка остановки 2 - проверка структуры ответа
    
    # Ошибка: KeyError - обращение по несуществующему ключу
    rate_value = mock_response["rates"]  # Такого ключа нет!
    
    # Кешируем результат (без проверки размера - утечка)
    API_CACHE[cache_key] = rate_value
    return rate_value

def convert_currency(amount, from_currency, to_currency):
    """Конвертация валюты с логической ошибкой"""
    
    # ============ breakpoint() №3: Перед получением курса ============
    breakpoint()  # Точка остановки 3 - проверка параметров конвертации
    
    rate = fetch_exchange_rate(from_currency, to_currency)
    
    # ============ breakpoint() №4: После получения курса ============
    breakpoint()  # Точка остановки 4 - проверка типа и значения rate
    
    # Ошибка: неверное преобразование типов
    result = amount * rate  # TypeError!
    
    return result

def process_currency_data(transactions):
    """Обработка списка транзакций"""
    results = []
    
    for idx, tx in enumerate(transactions):
        print(f"\n--- Обработка транзакции #{idx + 1} ---")
        
        # breakpoint() №5: Перед доступом к ключам
        breakpoint()  # Точка остановки 5 - проверка структуры транзакции
        
        # Ошибка: нет обработки отсутствующих ключей
        amount = tx["amount"]  # KeyError, если ключа нет
        from_currency = tx["from"]
        to_currency = tx["to"]
        
        print(f"Транзакция: {amount} {from_currency} -> {to_currency}")
        
        try:
            converted = convert_currency(amount, from_currency, to_currency)
            results.append({
                "original": tx,
                "converted": converted,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Ошибка при конвертации: {e}")
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
    
    print("=" * 60)
    print("НАЧАЛО ОТЛАДКИ С breakpoint()")
    print("=" * 60)
    print("Тестовые данные:", test_transactions)
    print("\nНачинаем обработку транзакций...")
    print("-" * 60)
    
    result = process_currency_data(test_transactions)
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ:")
    print("=" * 60)
    for idx, item in enumerate(result):
        print(f"{idx + 1}. {item}")
    

    snapshot = tracemalloc.take_snapshot()
    print("\n" + "=" * 60)
    print("ТОП-5 СТРОК ПО ПОТРЕБЛЕНИЮ ПАМЯТИ:")
    print("=" * 60)
    for stat in snapshot.statistics('lineno')[:5]:
        print(stat)
    
    print("\n" + "=" * 60)
    print("РАЗМЕР КЕША API_CACHE:", len(API_CACHE))
    print("СОДЕРЖИМОЕ КЕША:")
    for key, value in API_CACHE.items():
        print(f"  {key}: {value}")
    print("=" * 60)
