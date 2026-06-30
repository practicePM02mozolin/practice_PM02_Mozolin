#!/usr/bin/env python3
"""
JSON API Processor с отладкой памяти через tracemalloc
Этап 4: Полностью исправленная и улучшенная версия
"""
import requests
import math
import time
import json
import sys
import tracemalloc
import gc
import os
from typing import Optional, Dict, List, Any, Tuple
from collections import OrderedDict
from datetime import datetime

#КЛАСС КЕША С ОТСЛЕЖИВАНИЕМ ПАМЯТИ

class MemoryAwareCache:
    """Кеш с отслеживанием использования памяти"""
    
    def __init__(self, maxsize: int = 50, ttl: int = 60):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.ttl = ttl
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
        self.created_at = time.time()
        
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кеша"""
        self.total_requests += 1
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.cache.move_to_end(key)
                self.hits += 1
                return value
            else:
                del self.cache[key]
                self.misses += 1
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Сохранение значения в кеше"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, time.time())
        
        # Проверяем размер кеша
        if len(self.cache) > self.maxsize:
            old_key, _ = self.cache.popitem(last=False)
            
            # Отладочное сообщение
            if '--debug-memory' in sys.argv:
                print(f"[MEMORY DEBUG] Cache maxsize exceeded. Removed: {old_key[:50]}...")
    
    def clear(self) -> None:
        """Очистка кеша"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        total = self.hits + self.misses
    
        # Вычисляем примерный размер кеша в памяти
        cache_size_bytes = 0
        for key, (value, _) in self.cache.items():
            try:
                cache_size_bytes += sys.getsizeof(key)
                cache_size_bytes += sys.getsizeof(value)
            except:
                pass
        
        return {
            'size': len(self.cache),
            'maxsize': self.maxsize,
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': self.total_requests,
            'hit_rate': round((self.hits / total * 100) if total > 0 else 0, 2),
            'memory_usage_bytes': cache_size_bytes,
            'memory_usage_mb': round(cache_size_bytes / (1024 * 1024), 4),
            'age_seconds': round(time.time() - self.created_at, 1)
        }
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ

api_cache = MemoryAwareCache(maxsize=50, ttl=60)
request_counter = 0
successful_requests = 0
failed_requests = 0
start_time = None

# Для tracemalloc
memory_snapshots = []
tracemalloc_enabled = False

#ФУНКЦИИ ДЛЯ ОТЛАДКИ ПАМЯТИ

def start_memory_tracing():
    """Запуск трассировки памяти"""
    global tracemalloc_enabled
    if not tracemalloc_enabled:
        tracemalloc.start()
        tracemalloc_enabled = True
        print("[MEMORY] ✅ Tracemalloc started")
        print(f"[MEMORY] 📊 Initial memory usage: {get_memory_usage():.2f} MB")


def stop_memory_tracing():
    """Остановка трассировки памяти"""
    global tracemalloc_enabled
    if tracemalloc_enabled:
        tracemalloc.stop()
        tracemalloc_enabled = False
        print("[MEMORY] ⏹️ Tracemalloc stopped")


def get_memory_usage() -> float:
    """Получение текущего использования памяти в МБ"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        # Если psutil не установлен, используем tracemalloc
        if tracemalloc_enabled:
            snapshot = tracemalloc.take_snapshot()
            total = sum(stat.size for stat in snapshot.statistics('lineno'))
            return total / (1024 * 1024)
        return 0.0
def take_memory_snapshot(name: str = ""):
    """Создание снимка памяти"""
    if not tracemalloc_enabled:
        if '--trace-memory' in sys.argv:
            print("[WARNING] ⚠️ Tracemalloc not started. Use --trace-memory")
        return None
    snapshot = tracemalloc.take_snapshot()
    timestamp = time.time()
    memory_snapshots.append((name, snapshot, timestamp))
    
    # Анализ снимка
    print(f"\n📸 [MEMORY SNAPSHOT] {name}")
    print(f"   Time: {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}")
    print(f"   Total snapshots: {len(memory_snapshots)}")
    
    # Топ-10 выделений памяти по строкам
    top_stats = snapshot.statistics('lineno')
    
    print(f"\n   📊 Top 10 memory allocations by line:")
    for i, stat in enumerate(top_stats[:10], 1):
        size_mb = stat.size / (1024 * 1024)
        print(f"   {i:2d}. {stat} ({size_mb:.3f} MB)")
    
    # Топ-5 по файлам
    top_files = snapshot.statistics('filename')
    print(f"\n   📁 Top 5 memory allocations by file:")
    for i, stat in enumerate(top_files[:5], 1):
        size_mb = stat.size / (1024 * 1024)
        print(f"   {i:2d}. {stat} ({size_mb:.3f} MB)")
    
    # Общая статистика
    total_memory = sum(stat.size for stat in top_stats)
    print(f"\n   💾 Total memory in snapshot: {total_memory / (1024 * 1024):.2f} MB")
    print(f"   📌 Number of allocations: {len(top_stats)}")
    
    return snapshot
def compare_memory_snapshots():
    """Сравнение последних двух снимков памяти"""
    if len(memory_snapshots) < 2:
        print("[MEMORY] ℹ️ Need at least 2 snapshots to compare")
        return
    
    name1, snapshot1, time1 = memory_snapshots[-2]
    name2, snapshot2, time2 = memory_snapshots[-1]
    
    print(f"\n🔄 [MEMORY COMPARISON]")
    print(f"   From: {datetime.fromtimestamp(time1).strftime('%H:%M:%S')} ({name1})")
    print(f"   To:   {datetime.fromtimestamp(time2).strftime('%H:%M:%S')} ({name2})")
    print(f"   Duration: {time2 - time1:.2f}s")
    
    # Сравниваем снимки
    diff_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print(f"\n   📊 Top 10 memory changes:")
    has_changes = False
    total_diff = 0
    
    for i, stat in enumerate(diff_stats[:10], 1):
        if stat.size_diff != 0:
            has_changes = True
            sign = "+" if stat.size_diff > 0 else ""
            size_kb = stat.size_diff / 1024
            total_diff += stat.size_diff
            print(f"   {i:2d}. {stat} ({sign}{size_kb:.2f} KB)")
    
    if not has_changes:
        print("   ✅ No significant memory changes detected")
    
    # Общее изменение памяти
    print(f"\n   📈 Total memory change: {total_diff / (1024 * 1024):.3f} MB")
    
    if total_diff > 1024 * 1024:  # Больше 1MB
        print(f"   ⚠️  WARNING: Memory increased significantly!")
        print(f"   💡 SUGGESTION: Check for memory leaks in the code")
    elif total_diff > 0:
        print(f"   📈 Memory increased slightly")
    else:
        print(f"   ✅ Memory usage decreased or remained stable")

def analyze_cache_memory():
    """Анализ использования памяти кешем"""
    print(f"\n🗂️  [CACHE MEMORY ANALYSIS]")
    
    cache_stats = api_cache.get_stats()
    print(f"   📊 Cache Statistics:")
    print(f"      Size: {cache_stats['size']}/{cache_stats['maxsize']}")
    print(f"      Hits: {cache_stats['hits']}")
    print(f"      Misses: {cache_stats['misses']}")
    print(f"      Hit rate: {cache_stats['hit_rate']}%")
    print(f"      Memory usage: {cache_stats['memory_usage_mb']} MB ({cache_stats['memory_usage_bytes']} bytes)")
    print(f"      Age: {cache_stats['age_seconds']:.1f}s")
    
    # Детальный анализ каждого элемента кеша
    if cache_stats['size'] > 0:
        print(f"\n   📋 Cache items detail:")
        items_shown = 0
        total_size = 0
        
        for key, (value, timestamp) in list(api_cache.cache.items())[:5]:
            try:
                size = sys.getsizeof(key) + sys.getsizeof(value)
                total_size += size
                age = time.time() - timestamp
                print(f"      Key: {key[:40]}...")
                print(f"        Size: {size/1024:.2f} KB, Age: {age:.1f}s")
                items_shown += 1
            except:
                pass
        
        if cache_stats['size'] > 5:
            print(f"      ... and {cache_stats['size'] - 5} more items")
        
        avg_size = total_size / items_shown if items_shown > 0 else 0
        print(f"\n   📊 Average item size: {avg_size/1024:.2f} KB")


#МОК-ДАННЫЕ

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
}


def get_mock_response(url: str) -> Optional[Dict]:
    """Генерация мок-ответа для тестирования"""
    if "jsonplaceholder" in url:
        try:
            user_id = int(url.split('/')[-1])
            if user_id in MOCK_USERS:
                return {"data": {"user": MOCK_USERS[user_id]}}
            else:
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
        return None
    else:
        return {"data": {"user": {"id": 999, "name": "Test User", "email": "test@example.com"}}}


#ОСНОВНЫЕ ФУНКЦИИ

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
    """Получение данных с API с кешированием"""
    global request_counter, successful_requests, failed_requests, api_cache
    
    request_counter += 1
    
    # Проверяем кеш
    cached = api_cache.get(url)
    if cached:
        return cached
    
    try:
        if use_mock:
            response_data = get_mock_response(url)
            if response_data is None:
                failed_requests += 1
                print(f"⚠️  Warning: No mock data for {url}")
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
        
        if user_id is None:
            failed_requests += 1
            print(f"⚠️  Warning: No user ID for {url}")
            return None
        
        successful_requests += 1
        result = {'user_id': user_id, 'data': user_data}
        api_cache.set(url, result)
        return result
        
    except Exception as e:
        failed_requests += 1
        print(f"❌ Error for {url}: {e}")
        return None


#МАТЕМАТИЧЕСКИЕ ФУНКЦИИ

def calculate_ratio(a: float, b: float) -> float:
    """Вычисление соотношения с защитой от деления на ноль"""
    if b == 0:
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
    """Обработка списка URL с отладкой памяти"""
    global start_time
    results = []
    total_urls = len(urls)
    
    print(f"\n🚀 Processing {total_urls} URLs...")
    start_time = time.time()
    
    # Начальный снимок памяти
    if '--trace-memory' in sys.argv:
        take_memory_snapshot("Start of processing")
    
    for index, url in enumerate(urls):
        data = fetch_data(url)
        
        if data and data.get('user_id') is not None:
            processed = process_item(data)
            if processed:
                results.append(processed)
        
        # Прогресс каждые 10 итераций
        if (index + 1) % 10 == 0:
            elapsed = time.time() - start_time
            print(f"\n📊 Progress: {index + 1}/{total_urls}")
            print(f"   ⏱️  Elapsed: {elapsed:.2f}s")
            
            current_memory = get_memory_usage()
            print(f"   💾 Current memory: {current_memory:.2f} MB")
            
            cache_stats = api_cache.get_stats()
            print(f"   🗂️  Cache stats:")
            print(f"      Size: {cache_stats['size']}/{cache_stats['maxsize']}")
            print(f"      Memory: {cache_stats['memory_usage_mb']} MB")
            print(f"      Hit rate: {cache_stats['hit_rate']}%")
            
            # Снимок памяти каждые 10 итераций
            if '--trace-memory' in sys.argv:
                take_memory_snapshot(f"After {index + 1} requests")
    
    # Финальный снимок памяти
    if '--trace-memory' in sys.argv:
        take_memory_snapshot("End of processing")
        compare_memory_snapshots()
    
    total_time = time.time() - start_time
    print(f"\n✅ Completed in {total_time:.2f}s. Processed {len(results)} items")
    return results


def process_item(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обработка отдельного элемента"""
    if not data or 'user_id' not in data:
        return None
    
    user_id = data['user_id']
    raw_data = data.get('data', {})
    
    user_name = raw_data.get('name', 'Unknown')
    user_email = raw_data.get('email', 'no-email@example.com')
    
    # Вычисляем метрики
    ratio = calculate_ratio(user_id, 10)
    distance = calculate_distance(0, 0, user_id % 5, user_id // 5)
    percentage = calculate_percentage(user_id, 100)
    
    return {
        'user_id': user_id,
        'name': user_name,
        'email': user_email,
        'metrics': {
            'ratio': ratio,
            'distance': distance,
            'percentage': percentage
        }
    }

# ============== ТЕСТОВЫЕ ДАННЫЕ ==============

def generate_test_urls(count: int = 50) -> List[str]:
    """Генерация тестовых URL"""
    urls = []
    for i in range(1, count + 1):
        if i % 5 == 0:
            urls.append(f"https://httpbin.org/status/404?error={i}")
        else:
            urls.append(f"https://jsonplaceholder.typicode.com/users/{i}")
    return urls

# ============== СИМУЛЯЦИЯ УТЕЧЕК ПАМЯТИ ==============

def simulate_memory_leak():
    """Симуляция утечки памяти для демонстрации tracemalloc"""
    print("\n🧪 [DEMO] Simulating memory leak...")
    leak_list = []
    
    for i in range(5):
        # Создаем большие объекты
        leak_list.append([i] * 100000)
        
        if i % 2 == 0:
            current_mem = get_memory_usage()
            print(f"   Iteration {i}: memory = {current_mem:.2f} MB")
            
            if '--trace-memory' in sys.argv:
                take_memory_snapshot(f"Leak iteration {i}")
    
    print(f"⚠️  [WARNING] {len(leak_list)} objects retained in memory!")
    print(f"💡 [SUGGESTION] These objects should be cleared when no longer needed")
    return leak_list


# ============== ГЛАВНАЯ ФУНКЦИЯ ==============

def main():
    """Главная функция с отладкой памяти"""
    global api_cache, request_counter, successful_requests, failed_requests, memory_snapshots
    
    print("=" * 70)
    print("🔍 JSON API Processor with Memory Debugging (tracemalloc)")
    print("=" * 70)
    
    # Проверяем аргументы командной строки
    debug_modes = {
        '--trace-memory': 'Enable tracemalloc memory tracing',
        '--debug-memory': 'Enable memory debug messages',
        '--simulate-leak': 'Simulate memory leak for demonstration',
        '--analyze-cache': 'Analyze cache memory usage',
        '--real-api': 'Use real API (not mocks)',
        '--help': 'Show help'
    }
    
    active_modes = [mode for mode in debug_modes if mode in sys.argv]
    use_mock = '--real-api' not in sys.argv
    trace_memory = '--trace-memory' in sys.argv
    simulate_leak = '--simulate-leak' in sys.argv
    analyze_cache = '--analyze-cache' in sys.argv
    
    if '--help' in sys.argv:
        print("\n📖 Usage: python variant_11.py [OPTIONS]\n")
        print("Options:")
        for mode, desc in debug_modes.items():
            print(f"  {mode:<20} {desc}")
        print("\nExamples:")
        print("  python variant_11.py --trace-memory")
        print("  python variant_11.py --trace-memory --debug-memory")
        print("  python variant_11.py --trace-memory --simulate-leak")
        print("  python variant_11.py --analyze-cache")
        return
    
    print(f"\n⚙️  Active modes: {active_modes if active_modes else 'None'}")
    print(f"📡 Using: {'MOCKS' if use_mock else 'REAL API'}")
    print("-" * 70)
    
    # Сбрасываем счетчики
    request_counter = 0
    successful_requests = 0
    failed_requests = 0
    api_cache.clear()
    memory_snapshots.clear()
    
    # Запускаем tracemalloc
    if trace_memory:
        start_memory_tracing()
        gc.collect()
        print(f"[MEMORY] 🧹 After GC: {get_memory_usage():.2f} MB")
    
    # Генерируем тестовые URL
    test_urls = generate_test_urls(50)
    print(f"\n📋 Generated {len(test_urls)} test URLs")
    failed_urls_count = sum(1 for url in test_urls if "404" in url)
    print(f"   ℹ️  {failed_urls_count} URLs will fail (every 5th URL)")
    
    try:
        # Симуляция утечки памяти
        leak_objects = None
        if simulate_leak and trace_memory:
            leak_objects = simulate_memory_leak()
        
        # Обработка данных
        results = process_api_data(test_urls)
        
        # Анализ кеша
        if analyze_cache:
            analyze_cache_memory()
        
        # Выводим результаты
        print("\n" + "=" * 70)
        print(f"📊 FINAL RESULTS")
        print("=" * 70)
        
        print(f"\n📈 Statistics:")
        print(f"   Total requests: {request_counter}")
        print(f"   ✅ Successful: {successful_requests}")
        print(f"   ❌ Failed: {failed_requests}")
        print(f"   📦 Items processed: {len(results)}")
        
        if results:
            print(f"\n📝 Sample results (first 3):")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. User {result['user_id']}: {result['name']}")
                print(f"      Metrics: {result['metrics']}")
        
        # Статистика кеша
        cache_stats = api_cache.get_stats()
        print(f"\n🗂️  Cache Statistics:")
        print(f"   Size: {cache_stats['size']}/{cache_stats['maxsize']}")
        print(f"   Hits: {cache_stats['hits']}")
        print(f"   Misses: {cache_stats['misses']}")
        print(f"   Hit rate: {cache_stats['hit_rate']}%")
        print(f"   Memory usage: {cache_stats['memory_usage_mb']} MB")
        print(f"   Age: {cache_stats['age_seconds']:.1f}s")
        
        # Финальный анализ памяти
        if trace_memory:
            print("\n" + "-" * 70)
            print("💾 FINAL MEMORY ANALYSIS")
            print("-" * 70)
            
            final_memory = get_memory_usage()
            print(f"   Final memory usage: {final_memory:.2f} MB")
            
            # Проверяем наличие утечек
            if simulate_leak and leak_objects:
                print(f"\n⚠️  [WARNING] {len(leak_objects)} objects still in memory!")
                print(f"💡 [SUGGESTION] Use tracemalloc to find where objects are created")
            
            print("\n💡 MEMORY RECOMMENDATIONS:")
            print("   1. Use cache with TTL to limit memory growth")
            print("   2. Clear large objects when no longer needed")
            print("   3. Use generators instead of lists for large datasets")
            print("   4. Profile memory with tracemalloc regularly")
        
        # Останавливаем tracemalloc
        if trace_memory:
            stop_memory_tracing()
        
        print("\n✅ Program completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if trace_memory and tracemalloc_enabled:
            stop_memory_tracing()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("💡 Tip: Use --help to see available options")
        print("📌 Example: python variant_11.py --trace-memory")
        print("-" * 70)
    
    main()