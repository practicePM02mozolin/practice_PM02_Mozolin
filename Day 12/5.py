
#!/usr/bin/env python3
"""
JSON API Processor с исправлением логики
Этап 5: Полностью исправленная версия с защитой от всех ошибок
"""
import requests
import math
import time
import json
import sys
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

#НАСТРОЙКА ЛОГГИРОВАНИЯ

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

#ENUM ДЛЯ КАТЕГОРИЙ

class BMICategory(Enum):
    UNDERWEIGHT = "Underweight"
    NORMAL = "Normal weight"
    OVERWEIGHT = "Overweight"
    OBESE = "Obese"
    UNKNOWN = "Unknown"

class PerformanceLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EXCELLENT = "Excellent"
    UNKNOWN = "Unknown"

# ============== DATA CLASSES ==============

@dataclass
class BMICalculation:
    bmi: float = 0.0
    category: str = "Unknown"
    valid: bool = False
    error: Optional[str] = None

@dataclass
class UserMetrics:
    bmi: Optional[float] = None
    bmi_category: str = "Unknown"
    age_score: float = 0.0
    salary_ratio: float = 0.0
    performance_score: float = 0.0
    performance_level: str = "Unknown"
    valid: bool = False
    errors: List[str] = field(default_factory=list)

@dataclass
class ProcessedUser:
    user_id: int
    name: str
    email: str
    age: int
    salary: float
    metrics: UserMetrics
    warnings: List[str] = field(default_factory=list)

# ============== КЛАСС КЕША ==============

class SimpleCache:
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
    
# ============== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==============

api_cache = SimpleCache(maxsize=50)
request_counter = 0
successful_requests = 0
failed_requests = 0
all_warnings = []
all_errors = []

# ============== МОК-ДАННЫЕ ==============

MOCK_USERS = {
    1: {"id": 1, "name": "Leanne Graham", "email": "Sincere@april.biz", 
        "age": 28, "salary": 50000, "weight": 70, "height": 1.75},
    2: {"id": 2, "name": "Ervin Howell", "email": "Shanna@melissa.tv", 
        "age": 32, "salary": 60000, "weight": 75, "height": 1.80},
    3: {"id": 3, "name": "Clementine Bauch", "email": "Nathan@yesenia.net", 
        "age": 25, "salary": 45000, "weight": 60, "height": 1.65},
    4: {"id": 4, "name": "Patricia Lebsack", "email": "Julianne.OConner@kory.org", 
        "age": 40, "salary": 75000, "weight": 80, "height": 1.70},
    5: {"id": 5, "name": "Chelsey Dietrich", "email": "Lucio_Hettinger@annie.ca", 
        "age": 35, "salary": 0, "weight": 65, "height": 1.68},
    6: {"id": 6, "name": "Mrs. Dennis Schulist", "email": "Karley_Dach@jasper.info", 
        "age": 29, "salary": 55000, "weight": 68, "height": 1.72},
    7: {"id": 7, "name": "Kurtis Weissnat", "email": "Telly.Hoeger@billy.biz", 
        "age": 42, "salary": 80000, "weight": 85, "height": 1.78},
    8: {"id": 8, "name": "Nicholas Runolfsdottir V", "email": "Sherwood@rosamond.me", 
        "age": 0, "salary": 65000, "weight": 72, "height": 1.75},
    9: {"id": 9, "name": "Glenna Reichert", "email": "Chaim_McDermott@dana.io", 
        "age": 55, "salary": 90000, "weight": 78, "height": 1.65},
    10: {"id": 10, "name": "Clementina DuBuque", "email": "Rey.Padberg@karina.biz", 
         "age": 30, "salary": 70000, "weight": 62, "height": 1.60},
}

def get_mock_response(url: str) -> Optional[Dict]:
    """Генерация мок-ответа"""
    if "jsonplaceholder" in url:
        try:
            user_id = int(url.split('/')[-1])
            if user_id in MOCK_USERS:
                return {"data": {"user": MOCK_USERS[user_id]}}
            else:
                return {
                    "data": {
                        "user": {
                            "id": user_id,
                            "name": f"User {user_id}",
                            "email": f"user{user_id}@example.com",
                            "age": 20 + (user_id % 50),
                            "salary": 30000 + (user_id * 1000),
                            "weight": 60 + (user_id % 30),
                            "height": 1.60 + ((user_id % 20) / 100)
                        }
                    }
                }
        except ValueError:
            return None
    elif "httpbin.org/status/404" in url:
        return None
    else:
        return {
            "data": {
                "user": {
                    "id": 999,
                    "name": "Test User",
                    "email": "test@example.com",
                    "age": 25,
                    "salary": 50000,
                    "weight": 70,
                    "height": 1.75
                }
            }
        }

# ============== БЕЗОПАСНЫЕ МАТЕМАТИЧЕСКИЕ ФУНКЦИИ ==============

def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Безопасное деление"""
    if denominator == 0 or abs(denominator) < 1e-308:
        return default
    if math.isinf(numerator) or math.isinf(denominator):
        return default
    if math.isnan(numerator) or math.isnan(denominator):
        return default
    try:
        result = numerator / denominator
        return default if (math.isinf(result) or math.isnan(result)) else result
    except:
        return default

def safe_sqrt(value: float, default: float = 0.0) -> float:
    """Безопасное извлечение корня"""
    if value < 0:
        value = abs(value)
    if math.isinf(value) or math.isnan(value):
        return default
    try:
        result = math.sqrt(value)
        return default if math.isnan(result) else result
    except:
        return default

def safe_round(value: float, decimals: int = 2) -> float:
    """Безопасное округление"""
    if math.isnan(value) or math.isinf(value):
        return 0.0
    try:
        return round(value, decimals)
    except:
        return value

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Ограничение значения"""
    if math.isnan(value) or math.isinf(value):
        return min_val
    return max(min_val, min(value, max_val))

# ============== ФУНКЦИИ РАСЧЕТА ==============

def calculate_bmi(weight: float, height: float) -> BMICalculation:
    """Расчет ИМТ"""
    if weight <= 0:
        return BMICalculation(valid=False, error=f"Invalid weight: {weight}")
    if height <= 0:
        return BMICalculation(valid=False, error=f"Invalid height: {height}")
    
    weight = min(weight, 500.0)
    height = min(height, 3.0)
    
    height_squared = height * height
    if height_squared <= 0:
        return BMICalculation(valid=False, error="Height squared is zero")
    
    bmi = safe_division(weight, height_squared, 0.0)
    if bmi <= 0:
        return BMICalculation(valid=False, error=f"Invalid BMI: {bmi}")
    
    if bmi < 18.5:
        category = BMICategory.UNDERWEIGHT.value
    elif bmi < 25:
        category = BMICategory.NORMAL.value
    elif bmi < 30:
        category = BMICategory.OVERWEIGHT.value
    else:
        category = BMICategory.OBESE.value
    
    return BMICalculation(bmi=safe_round(bmi, 1), category=category, valid=True)

def calculate_user_metrics(user_data: Dict[str, Any]) -> UserMetrics:
    """Расчет метрик пользователя"""
    errors = []
    
    age = user_data.get('age', 25)
    salary = user_data.get('salary', 50000)
    weight = user_data.get('weight', 70)
    height = user_data.get('height', 1.75)
    
    # BMI
    bmi_result = calculate_bmi(weight, height)
    bmi_value = bmi_result.bmi if bmi_result.valid else None
    bmi_category = bmi_result.category if bmi_result.valid else BMICategory.UNKNOWN.value
    if not bmi_result.valid and bmi_result.error:
        errors.append(f"BMI Error: {bmi_result.error}")
    
    # Age score
    if age < 0:
        errors.append(f"Negative age: {age}")
        age = abs(age)
    if age > 150:
        errors.append(f"Suspicious age: {age}")
        age = 150
    age_score = clamp(safe_division(age, 100, 0.0), 0.0, 1.0)
    
    # Salary ratio
    if salary < 0:
        errors.append(f"Negative salary: {salary}")
        salary = abs(salary)
    salary_ratio = clamp(safe_division(salary, 100000, 0.0), 0.0, 2.0)
    
    # Performance score
    components = []
    
    if bmi_value is not None and 0 < bmi_value < 50:
        bmi_score = clamp(1 - abs(bmi_value - 22) / 22, 0.0, 1.0)
        components.append(bmi_score)
    
    age_performance = clamp(1 - abs(age_score - 0.35) / 0.35, 0.0, 1.0)
    components.append(age_performance)
    
    salary_performance = min(1.0, salary_ratio)
    components.append(salary_performance)
    
    performance_score = sum(components) / len(components) if components else 0.0
    performance_score = clamp(performance_score, 0.0, 1.0)
    
    # Performance level
    if performance_score >= 0.8:
        level = PerformanceLevel.EXCELLENT.value
    elif performance_score >= 0.6:
        level = PerformanceLevel.HIGH.value
    elif performance_score >= 0.4:
        level = PerformanceLevel.MEDIUM.value
    else:
        level = PerformanceLevel.LOW.value
    
    return UserMetrics(
        bmi=bmi_value,
        bmi_category=bmi_category,
        age_score=safe_round(age_score, 2),
        salary_ratio=safe_round(salary_ratio, 2),
        performance_score=safe_round(performance_score, 2),
        performance_level=level,
        valid=bool(components),
        errors=errors
    )

# ============== ОСНОВНЫЕ ФУНКЦИИ ==============
def safe_json_parse(response) -> Dict[str, Any]:
    """Безопасный парсинг JSON"""
    try:
        if hasattr(response, 'json'):
            return response.json()
        elif isinstance(response, dict):
            return response
        return {}
    except:
        return {}

def fetch_data(url: str, timeout: int = 5, use_mock: bool = True) -> Optional[Dict[str, Any]]:
    """Получение данных"""
    global request_counter, successful_requests, failed_requests
    
    request_counter += 1
    
    cached = api_cache.get(url)
    if cached:
        return cached
    
    try:
        if use_mock:
            response_data = get_mock_response(url)
            if response_data is None:
                failed_requests += 1
                logger.warning(f"No mock data for {url}")
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
            return None
        
        successful_requests += 1
        result = {'user_id': user_id, 'data': user_data}
        api_cache.set(url, result)
        return result
        
    except Exception as e:
        failed_requests += 1
        logger.error(f"Error for {url}: {e}")
        return None

def process_item(data: Dict[str, Any]) -> Optional[ProcessedUser]:
    """Обработка элемента"""
    global all_warnings, all_errors
    
    if not data or 'user_id' not in data:
        return None
    
    user_id = data['user_id']
    user_data = data.get('data', {})
    
    name = user_data.get('name', 'Unknown')
    email = user_data.get('email', 'unknown@example.com')
    age = user_data.get('age', 25)
    salary = user_data.get('salary', 50000)
    warnings = []
    
    if age < 0:
        warnings.append(f"Negative age: {age}")
        age = abs(age)
    if age > 150:
        warnings.append(f"Suspicious age: {age}")
        age = 150
    
    if salary < 0:
        warnings.append(f"Negative salary: {salary}")
        salary = abs(salary)
    
    metrics = calculate_user_metrics(user_data)
    
    for error in metrics.errors:
        all_errors.append(f"User {user_id}: {error}")
    
    return ProcessedUser(
        user_id=user_id,
        name=name,
        email=email,
        age=age,
        salary=float(salary),
        metrics=metrics,
        warnings=warnings
    )

def process_api_data(urls: List[str]) -> List[ProcessedUser]:
    """Обработка списка URL"""
    results = []
    total_urls = len(urls)
    
    logger.info(f"Processing {total_urls} URLs...")
    
    for index, url in enumerate(urls):
        data = fetch_data(url)
        if data and data.get('user_id') is not None:
            processed = process_item(data)
            if processed:
                results.append(processed)
        
        if (index + 1) % 10 == 0:
            logger.info(f"Progress: {index + 1}/{total_urls}")
    
    logger.info(f"Completed. Processed {len(results)} items")
    return results

def generate_test_urls(count: int = 30) -> List[str]:
    """Генерация тестовых URL"""
    urls = []
    for i in range(1, count + 1):
        if i % 5 == 0:
            urls.append(f"https://httpbin.org/status/404?error={i}")
        else:
            urls.append(f"https://jsonplaceholder.typicode.com/users/{i}")
    return urls

# ============== ТЕСТЫ ==============
def run_tests():
    """Запуск тестов"""
    print("\n" + "=" * 60)
    print("🧪 RUNNING TESTS")
    print("=" * 60)
    
    # Тест safe_division
    print("\n📊 safe_division:")
    for num, den in [(10, 2), (10, 0), (-10, 2), (float('inf'), 2)]:
        result = safe_division(num, den)
        print(f"  {num}/{den} = {result}")
    
    # Тест safe_sqrt
    print("\n📊 safe_sqrt:")
    for val in [25, -16, float('inf')]:
        result = safe_sqrt(val)
        print(f"  sqrt({val}) = {result:.2f}")
    
    # Тест calculate_bmi
    print("\n📊 calculate_bmi:")
    for weight, height in [(70, 1.75), (0, 1.75), (70, 0)]:
        result = calculate_bmi(weight, height)
        if result.valid:
            print(f"  BMI({weight}kg, {height}m) = {result.bmi} ({result.category})")
        else:
            print(f"  BMI({weight}kg, {height}m) = Error: {result.error}")
    
    print("\n" + "=" * 60)
    print("✅ Tests completed")
    print("=" * 60)

# ============== ГЛАВНАЯ ФУНКЦИЯ ==============
def main():
    """Главная функция"""
    global all_warnings, all_errors
    
    print("=" * 70)
    print("🔧 API Processor - Fixed Logic (Stage 5)")
    print("🛡️  Safety: Division by Zero, Negative Sqrt, etc.")
    print("=" * 70)
    
    if '--test' in sys.argv:
        run_tests()
        return
    
    if '--help' in sys.argv:
        print("\nUsage: python variant_11.py [OPTIONS]")
        print("\nOptions:")
        print("  --test          Run safety tests")
        print("  --real-api      Use real API (not mocks)")
        print("  --help          Show this help")
        return
    
    use_mock = '--real-api' not in sys.argv
    
    print(f"\n📡 Using: {'MOCKS' if use_mock else 'REAL API'}")
    print("-" * 70)
    
    # Сброс счетчиков
    global request_counter, successful_requests, failed_requests
    request_counter = 0
    successful_requests = 0
    failed_requests = 0
    all_warnings = []
    all_errors = []
    api_cache.cache.clear()
    
    test_urls = generate_test_urls(30)
    print(f"\n📋 Generated {len(test_urls)} test URLs")
    failed_urls = sum(1 for url in test_urls if "404" in url)
    print(f"   ℹ️  {failed_urls} URLs will fail")
    
    print("\n🛡️  Active Safety Features:")
    print("   ✅ Division by zero protection")
    print("   ✅ Negative sqrt protection")
    print("   ✅ BMI validation")
    print("   ✅ Age/Salary validation")
    print("   ✅ Performance classification")
    print("-" * 70)
    
    try:
        start_time = time.time()
        results = process_api_data(test_urls)
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        
        print(f"\n📈 Statistics:")
        print(f"   Total requests: {request_counter}")
        print(f"   ✅ Successful: {successful_requests}")
        print(f"   ❌ Failed: {failed_requests}")
        print(f"   📦 Items processed: {len(results)}")
        print(f"   ⏱️  Time: {elapsed:.2f}s")
        
        if results:
            print(f"\n📝 Sample results (first 3):")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. User {result.user_id}: {result.name}")
                print(f"      Age: {result.age}, Salary: {result.salary}")
                if result.metrics.bmi:
                    print(f"      BMI: {result.metrics.bmi} ({result.metrics.bmi_category})")
                print(f"      Performance: {result.metrics.performance_score} ({result.metrics.performance_level})")
        
        cache_stats = api_cache.get_stats()
        print(f"\n🗂️  Cache:")
        print(f"   Size: {cache_stats['size']}/{cache_stats['maxsize']}")
        print(f"   Hit rate: {cache_stats['hit_rate']}%")
        
        expected = len(test_urls) - failed_urls
        print(f"\n✅ Expected: {expected}, Got: {successful_requests}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("💡 Tip: Use --help for options")
        print("📌 Example: python variant_11.py --test")
        print("-" * 70)
    main()