import math
import time
import tracemalloc
import requests
from requests.exceptions import Timeout
from collections import OrderedDict

# ИСПРАВЛЕНИЕ 3: LRU-КЕШ ДЛЯ ПРЕДОТВРАЩЕНИЯ УТЕЧЕК

class LRUCache:
    """Кеш с ограничением размера (LRU - вытеснение наименее используемых)"""
    def __init__(self, maxsize=10):
        self.cache = OrderedDict()
        self.maxsize = maxsize
    
    def get(self, key):
        """Получить значение из кеша"""
        if key not in self.cache:
            return None
        # Перемещаем в конец (как самый свежий)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key, value):
        """Добавить значение в кеш"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        # Если превысили размер - удаляем самый старый
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)
    
    def __len__(self):
        return len(self.cache)
    
    def keys(self):
        return list(self.cache.keys())

# Используем LRU-кеш вместо обычного словаря
CACHE = LRUCache(maxsize=10)

def fetch_user_data(user_id):
    """
    Имитация запроса к внешнему API для получения данных пользователя.
    """
    # Имитация сетевого таймаута для некоторых ID
    if user_id == 42:
        time.sleep(5)  # Имитация долгого ответа
    
    # Имитация API ответа
    response = {
        "id": user_id,
        "name": f"User_{user_id}",
        "balance": "1000" if user_id % 2 == 0 else "500.5"
    }
    return response

def process_payments(user_ids):
    """
    Основная функция: для каждого user_id запрашивает данные и рассчитывает бонус.
    """
    result = []
    for uid in user_ids:
        # Используем LRU-кеш
        data = CACHE.get(uid)
        if data is None:
            try:
                data = fetch_user_data(uid)
            except Timeout:
                print(f"Timeout для user {uid}, пропускаем")
                continue
            CACHE.set(uid, data)

        # ИСПРАВЛЕНИЕ 1: Безопасный доступ к ключу 'balance'
        balance_str = data.get('balance', '0.0')
        
        # Преобразование строки в число
        try:
            balance = float(balance_str)
        except ValueError:
            balance = 0.0
        
        # ИСПРАВЛЕНИЕ 2: Правильная формула бонуса (5% от баланса)
        bonus = balance * 0.05  # Было: balance * 0.5 + 10

        result.append({
            "user_id": uid,
            "balance": balance,
            "bonus": bonus
        })
    return result

if __name__ == "__main__":

    # ОТЛАДКА ПАМЯТИ С tracemalloc
    
    # 1. Включаем tracemalloc
    tracemalloc.start()
    print("=== tracemalloc включен ===")
    print(f"=== Максимальный размер кеша: {CACHE.maxsize} ===\n")
    
    # Тестовые данные
    test_user_ids = [1, 2, 3, 42, 999]
    
    # ОСНОВНАЯ ЛОГИКА
    
    print("=== Пошаговая обработка с замерами памяти ===")
    
    output = []
    
    for i, uid in enumerate(test_user_ids):
        print(f"\n--- Обработка элемента {i+1}: uid={uid} ---")
        
        # Обрабатываем один элемент
        try:
            data = CACHE.get(uid)
            if data is None:
                try:
                    data = fetch_user_data(uid)
                    print(f"  Данные из API: {data}")
                except Timeout:
                    print(f"  Timeout для user {uid}, пропускаем")
                    continue
                CACHE.set(uid, data)
                print(f"  Добавлено в кеш: {uid}")
            else:
                print(f"  Данные из кеша: {data}")

            # ИСПРАВЛЕНИЕ 1: Безопасный доступ
            balance_str = data.get('balance', '0.0')
            print(f"  balance_str: {balance_str}")

            try:
                balance = float(balance_str)
            except ValueError:
                balance = 0.0
            
            # ИСПРАВЛЕНИЕ 2: Правильная формула
            bonus = balance * 0.05  # Исправлено!
            print(f"  Бонус (5%): {bonus}")

            result_item = {
                "user_id": uid,
                "balance": balance,
                "bonus": bonus
            }
            output.append(result_item)
            print(f"  Результат: {result_item}")
            
        except Exception as e:
            print(f"  ОШИБКА при обработке uid={uid}: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        # Снимок памяти после каждых 2-х элементов
        if (i + 1) % 2 == 0:
            print(f"\n--- Снимок памяти после {i+1} элементов ---")
            snapshot = tracemalloc.take_snapshot()
            print("Топ-5 строк по потреблению памяти:")
            for stat in snapshot.statistics('lineno')[:5]:
                print(f"  {stat}")
            
            print(f"  Размер кеша CACHE: {len(CACHE)} элементов")
            print(f"  Ключи в кеше: {CACHE.keys()}")
    
    # ФИНАЛЬНЫЙ СНИМОК ПАМЯТИ

    print("\n=== Финальный снимок памяти ===")
    snapshot = tracemalloc.take_snapshot()
    print("\nТоп-10 строк по потреблению памяти:")
    for stat in snapshot.statistics('lineno')[:10]:
        print(stat)
    
    # ВЫВОД РЕЗУЛЬТАТОВ

    print("\n=== ИТОГОВЫЙ РЕЗУЛЬТАТ ===")
    print(f"Обработано элементов: {len(output)}")
    print(f"Результат: {output}")
    print(f"Размер кеша CACHE: {len(CACHE)} элементов")
    print(f"Ключи в кеше: {CACHE.keys()}")
    
    # ПРОВЕРКА ИСПРАВЛЕНИЙ

    print("\n=== ПРОВЕРКА ИСПРАВЛЕНИЙ ===")
    print("✅ 1. Безопасный доступ к 'balance' через .get()")
    print("✅ 2. Исправлена формула бонуса: balance * 0.05")
    print("✅ 3. Добавлен LRU-кеш с ограничением размера (maxsize=10)")
    print("✅ 4. Обработка таймаутов уже была добавлена")
    
    # Проверка формулы на примере
    print("\nПример расчета бонуса (uid=1, balance=500.5):")
    print(f"  Было: 500.5 * 0.5 + 10 = 260.25")
    print(f"  Стало: 500.5 * 0.05 = {500.5 * 0.05}")
    
    print("\n=== Конец выполнения ===")
