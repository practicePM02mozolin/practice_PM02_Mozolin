#!/usr/bin/env python3
"""
JSON API Processor с условными точками останова
ИСПРАВЛЕННАЯ ВЕРСИЯ - правильная статистика кеша
"""
import requests
import math
import time
import json
import sys
from typing import Optional, Dict, List, Any

# КЕШ С ОГРАНИЧЕНИЕМ

class SimpleCache:
    """Простой кеш с ограничением размера и правильной статистикой"""
    
    def __init__(self, maxsize: int = 50):
        self.cache = {}
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
    
    def get(self, key: str) -> Optional[Any]:
        self.total_requests += 1
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        if len(self.cache) >= self.maxsize:
            # FIFO: удаляем первый элемент
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[key] = value
    
    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        return {
            'size': len(self.cache),
            'maxsize': self.maxsize,
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': self.total_requests,
            'hit_rate': round((self.hits / total * 100) if total > 0 else 0, 2)
        }

# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ

api_cache = SimpleCache(maxsize=50)
request_counter = 0
successful_requests = 0
failed_requests = 0

# ============== МОК-ДАННЫЕ ==============

MOCK_USERS = {
    1: {"id": 1, "name": "Leanne Graham", "email": "Sincere@april.biz"},
    2: {"id": 2, "name": "Ervin Howell", "email": "Shanna@melissa.tv"},
    3: {"id": 3, "name": "Clementine Bauch", "email": "Nathan@yesenia.net"},
    4: {"id": 4, "name": "Patricia Lebsack", "email": "Julianne.OConner@kory.org"},
    5: {"id": 5, "name": "Chelsey Dietrich", "email": "Lucio_Hettinger@annie.ca"},
    6: {"id": 6, "name": "Mrs. Dennis Schulist", "email": "Karley_Dach@jasper.info"},
    7: {"id": 7, "name": "Kurtis Weissnat", "email": "Telly.Hoeger@billy.biz"},
    8: {"id": 8, "name": "Nicholas Runolfsdottir V", "email": "Sherwood@rosamond.me"},
    9: {"id": 9, "name": "Glenna Reichert", "email": "Chaim_McDermott@dana.io"},
    10: {"id": 10, "name": "Clementina DuBuque", "email": "Rey.Padberg@karina.biz"},
    11: {"id": 11, "name": "User 11", "email": "user11@example.com"},
    12: {"id": 12, "name": "User 12", "email": "user12@example.com"},
    13: {"id": 13, "name": "User 13", "email": "user13@example.com"},
    14: {"id": 14, "name": "User 14", "email": "user14@example.com"},
    15: {"id": 15, "name": "User 15", "email": "user15@example.com"},
}

def get_mock_response(url: str) -> Optional[Dict]:
    """Генерация мок-ответа для тестирования"""
    if "jsonplaceholder" in url:
        try:
            user_id = int(url.split('/')[-1])
            if user_id in MOCK_USERS:
                return {"data": {"user": MOCK_USERS[user_id]}}
            else:
                # Для ID > 15 используем альтернативную структуру
                return {
                    "data": {
                        "id": user_id,
                        "name": f"User {user_id}",
                        "email": f"user{user_id}@example.com"
                    }
                }
        except ValueError:
            return None
    elif "httpbin.org/status/404" in url:
        # Симулируем ошибку 404
        return None
    else:
        return {"data": {"user": {"id": 999, "name": "Test User", "email": "test@example.com"}}}

# ============== ОСНОВНЫЕ ФУНКЦИИ ==============

def safe_json_parse(response) -> Dict[str, Any]:
    """Безопасный парсинг JSON"""
    try:
        if hasattr(response, 'json'):
            return response.json()
        elif isinstance(response, dict):
            return response
        return {}
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return {}

def fetch_data(url: str, timeout: int = 5, use_mock: bool = True) -> Optional[Dict[str, Any]]:
    """
    Получение данных с API
    Содержит условные точки останова для отладки
    """
    global request_counter, successful_requests, failed_requests, api_cache
    
    request_counter += 1
    
    # Проверяем кеш
    cached = api_cache.get(url)
    if cached:
        print(f"[CACHE HIT] {url}")
        return cached
    
    #УСЛОВНАЯ ТОЧКА ОСТАНОВА 1
    # Остановка каждые 10 запросов
    # Запуск: python variant_11.py --debug
    if request_counter % 10 == 0 and '--debug' in sys.argv:
        print(f"\n{'='*60}")
        print(f"[DEBUG] BREAKPOINT: Request #{request_counter}")
        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] Cache size: {len(api_cache.cache)}")
        print(f"{'='*60}")
        breakpoint()
    
    try:
        if use_mock:
            response_data = get_mock_response(url)
            if response_data is None:
                failed_requests += 1
                # ===== УСЛОВНАЯ ТОЧКА ОСТАНОВА 2 =====
                # Остановка при ошибке 404
                # Запуск: python variant_11.py --debug-errors
                if '--debug-errors' in sys.argv:
                    print(f"\n{'='*60}")
                    print(f"[DEBUG] BREAKPOINT: HTTP 404 Error")
                    print(f"[DEBUG] URL: {url}")
                    print(f"{'='*60}")
                    breakpoint()
                print(f"Warning: No data for {url}")
                return None
            
            class MockResponse:
                def __init__(self, data):
                    self._data = data
                    self.status_code = 200
                def json(self):
                    return self._data
                def raise_for_status(self):
                    pass
            
            response = MockResponse(response_data)
        else:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        
        data = safe_json_parse(response)
        if not data:
            failed_requests += 1
            return None
        
        # Извлекаем user_id
        user_id = None
        user_data = {}
        
        if 'data' in data:
            if 'user' in data['data']:
                user_info = data['data']['user']
                if isinstance(user_info, dict):
                    user_id = user_info.get('id')
                    user_data = user_info
            elif 'id' in data['data']:
                user_id = data['data']['id']
                user_data = data['data']
        
        #УСЛОВНАЯ ТОЧКА ОСТАНОВА 3
        # Остановка при отсутствии user_id
        # Запуск: python variant_11.py --debug-keys
        if user_id is None and '--debug-keys' in sys.argv:
            print(f"\n{'='*60}")
            print(f"[DEBUG] BREAKPOINT: Missing user_id")
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] Response: {json.dumps(data, indent=2)[:500]}")
            print(f"{'='*60}")
            breakpoint()
        
        if user_id is None:
            failed_requests += 1
            print(f"Warning: No user ID for {url}")
            return None
        
        successful_requests += 1
        result = {'user_id': user_id, 'data': user_data}
        api_cache.set(url, result)
        return result
        
    except Exception as e:
        failed_requests += 1
        print(f"Error for {url}: {e}")
        return None

# ============== МАТЕМАТИЧЕСКИЕ ФУНКЦИИ ==============

def calculate_ratio(a: float, b: float) -> float:
    """Вычисление соотношения с защитой от деления на ноль"""
    if b == 0:
        # ===== УСЛОВНАЯ ТОЧКА ОСТАНОВА 4 =====
        # Остановка при делении на ноль
        # Запуск: python variant_11.py --debug-math
        if '--debug-math' in sys.argv:
            print(f"\n{'='*60}")
            print(f"[DEBUG] BREAKPOINT: Division by zero")
            print(f"[DEBUG] a={a}, b={b}")
            print(f"{'='*60}")
            breakpoint()
        return 0.0
    return a / b

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Вычисление расстояния между точками"""
    dx = x2 - x1
    dy = y2 - y1
    squared = dx*dx + dy*dy
    if squared < 0:
        squared = 0
    return math.sqrt(squared)

def calculate_percentage(part: float, total: float) -> float:
    """Вычисление процента с защитой"""
    if total == 0:
        return 0.0
    return (part / total) * 100

# ============== ОБРАБОТКА ДАННЫХ ==============

def process_api_data(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Обработка списка URL
    Содержит условные точки останова для отладки
    """
    results = []
    total_urls = len(urls)
    
    print(f"\nProcessing {total_urls} URLs...")
    print("-" * 60)
    
    for index, url in enumerate(urls):
        # ===== УСЛОВНАЯ ТОЧКА ОСТАНОВА 5 =====
        # Остановка на 5-й итерации (индекс 4)
        # Запуск: python variant_11.py --debug-specific
        if index == 4 and '--debug-specific' in sys.argv:
            print(f"\n{'='*60}")
            print(f"[DEBUG] BREAKPOINT: Specific iteration #{index}")
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] Results so far: {len(results)}")
            print(f"{'='*60}")
            breakpoint()
        
        # ===== УСЛОВНАЯ ТОЧКА ОСТАНОВА 6 =====
        # Остановка на проблемных URL
        # Запуск: python variant_11.py --debug-errors
        if ('error' in url.lower() or '404' in url) and '--debug-errors' in sys.argv:
            print(f"\n{'='*60}")
            print(f"[DEBUG] BREAKPOINT: Problematic URL")
            print(f"[DEBUG] URL: {url}")
            print(f"{'='*60}")
            breakpoint()
        
        # ===== УСЛОВНАЯ ТОЧКА ОСТАНОВА 7 =====
        # Остановка при медленных запросах
        # Запуск: python variant_11.py --debug-performance
        if '--debug-performance' in sys.argv:
            start_time = time.time()
            data = fetch_data(url)
            elapsed = time.time() - start_time
            if elapsed > 1.0:
                print(f"\n{'='*60}")
                print(f"[DEBUG] BREAKPOINT: Slow request")
                print(f"[DEBUG] URL: {url}")
                print(f"[DEBUG] Elapsed: {elapsed:.2f}s")
                print(f"{'='*60}")
                breakpoint()
        else:
            data = fetch_data(url)
        
        if data and data.get('user_id'):
            processed = process_item(data)
            if processed:
                results.append(processed)
        
        # Прогресс каждые 10 итераций
        if (index + 1) % 10 == 0:
            print(f"\nProgress: {index + 1}/{total_urls}")
            stats = api_cache.get_stats()
            print(f"Cache stats:")
            print(f"  Size: {stats['size']}/{stats['maxsize']}")
            print(f"  Hits: {stats['hits']}")
            print(f"  Misses: {stats['misses']}")
            print(f"  Hit rate: {stats['hit_rate']}%")
            print(f"  Total requests to cache: {stats['total_requests']}")
            print("-" * 60)
    
    print(f"\nCompleted. Processed {len(results)} items")
    return results

def process_item(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обработка отдельного элемента"""
    if not data or 'user_id' not in data:
        return None
    
    user_id = data['user_id']
    user_data = data.get('data', {})
    
    return {
        'user_id': user_id,
        'name': user_data.get('name', 'Unknown'),
        'email': user_data.get('email', 'unknown@example.com'),
        'metrics': {
            'ratio': calculate_ratio(user_id, 10),
            'distance': calculate_distance(0, 0, user_id % 5, user_id // 5),
            'percentage': calculate_percentage(user_id, 100)
        }
    }

def generate_test_urls(count: int = 30) -> List[str]:
    """Генерация тестовых URL"""
    urls = []
    for i in range(1, count + 1):
        if i % 5 == 0:
            # Каждый 5-й URL - ошибка 404
            urls.append(f"https://httpbin.org/status/404?error={i}")
        else:
            urls.append(f"https://jsonplaceholder.typicode.com/users/{i}")
    return urls

# ============== ГЛАВНАЯ ФУНКЦИЯ ==============

def main():
    """Главная функция с настройкой режимов отладки"""
    global request_counter, successful_requests, failed_requests
    
    print("=" * 60)
    print("API Processor with Conditional Breakpoints")
    print("=" * 60)
    
    # Проверяем аргументы
    use_mock = '--real-api' not in sys.argv
    
    if '--help' in sys.argv:
        print("\nUsage: python variant_11.py [OPTIONS]")
        print("\nOPTIONS:")
        print("  --debug              Stop every 10 requests")
        print("  --debug-errors       Stop on HTTP errors and problematic URLs")
        print("  --debug-keys         Stop on missing keys in JSON")
        print("  --debug-math         Stop on mathematical errors")
        print("  --debug-specific     Stop on 5th iteration")
        print("  --debug-performance  Stop on slow requests (>1s)")
        print("  --real-api           Use real API (not mocks)")
        print("  --help               Show this help")
        print("\nEXAMPLES:")
        print("  python variant_11.py --debug")
        print("  python variant_11.py --debug --debug-errors")
        print("  python variant_11.py --debug-specific --debug-math")
        print("  python variant_11.py --debug --debug-errors --debug-specific")
        return
    
    # Активные режимы
    active_modes = [a for a in sys.argv if a.startswith('--') and a not in ['--real-api', '--help']]
    
    print(f"\nActive modes: {active_modes if active_modes else 'None'}")
    print(f"Using: {'MOCKS' if use_mock else 'REAL API'}")
    print("-" * 60)
    
    # Показываем доступные точки останова
    print("\nConditional breakpoints configured:")
    print("  1. Every 10 requests (--debug)")
    print("  2. HTTP errors (--debug-errors)")
    print("  3. Missing 'user' key (--debug-keys)")
    print("  4. Division by zero (--debug-math)")
    print("  5. 5th iteration (--debug-specific)")
    print("  6. Problematic URLs (--debug-errors)")
    print("  7. Slow requests >1s (--debug-performance)")
    print("-" * 60)
    
    # Генерируем URL
    urls = generate_test_urls(30)
    print(f"\nGenerated {len(urls)} test URLs")
    print(f"First 5 URLs: {urls[:5]}")
    print(f"Note: URLs with '404' will fail (6 URLs total)")
    print("-" * 60)
    
    # Сбрасываем счетчики
    request_counter = 0
    successful_requests = 0
    failed_requests = 0
    api_cache.cache.clear()
    api_cache.hits = 0
    api_cache.misses = 0
    api_cache.total_requests = 0
    
    try:
        start_time = time.time()
        
        # Обрабатываем данные
        results = process_api_data(urls)
        
        elapsed_time = time.time() - start_time
        
        # Выводим результаты
        print("\n" + "=" * 60)
        print(f"FINAL RESULTS")
        print("=" * 60)
        
        print(f"\nStatistics:")
        print(f"  Total URLs processed: {len(urls)}")
        print(f"  Successful requests: {successful_requests}")
        print(f"  Failed requests: {failed_requests}")
        print(f"  Items processed: {len(results)}")
        print(f"  Time elapsed: {elapsed_time:.2f}s")
        
        cache_stats = api_cache.get_stats()
        print(f"\nCache Statistics:")
        print(f"  Cache size: {cache_stats['size']}/{cache_stats['maxsize']}")
        print(f"  Cache hits: {cache_stats['hits']}")
        print(f"  Cache misses: {cache_stats['misses']}")
        print(f"  Hit rate: {cache_stats['hit_rate']}%")
        print(f"  Total requests to cache: {cache_stats['total_requests']}")
        
        if results:
            print(f"\nSample results (first 5):")
            for i, r in enumerate(results[:5], 1):
                print(f"  {i}. User {r['user_id']}: {r['name']}")
                print(f"     Email: {r['email']}")
                print(f"     Metrics: {r['metrics']}")
        
        # Проверяем корректность
        expected_success = len(urls) - 6  # 6 URLs с 404
        print(f"\nVerification:")
        print(f"  Expected successful: {expected_success}")
        print(f"  Actual successful: {successful_requests}")
        if successful_requests == expected_success:
            print("  ✓ All requests processed correctly!")
        else:
            print(f"  ✗ Mismatch! Expected {expected_success}, got {successful_requests}")
        
        print("\nProgram completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

#ТОЧКА ВХОДА

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Tip: Use --help to see available options")
        print("Example: python variant_11.py --debug")
        print("-" * 60)
    
    main()
