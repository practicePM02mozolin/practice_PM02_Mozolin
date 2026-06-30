#!/usr/bin/env python3
"""
test_backup.py — тестовый скрипт резервного копирования БЕЗ Elasticsearch
Имитирует создание бэкапа и формирует отчёт в формате JSON
"""

import json
import hashlib
import time
import random
from datetime import datetime
import os

# Настройка путей для сохранения отчётов
REPORT_DIR = "backup_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def generate_random_data(size_mb=5):
    """Генерация случайных тестовых данных"""
    data = {
        "indices": [
            {
                "name": f"logs-{datetime.now().strftime('%Y.%m.%d')}",
                "doc_count": random.randint(1000, 10000),
                "size_mb": random.randint(10, 500)
            },
            {
                "name": f"metrics-{datetime.now().strftime('%Y.%m.%d')}",
                "doc_count": random.randint(500, 5000),
                "size_mb": random.randint(5, 200)
            },
            {
                "name": f"security-{datetime.now().strftime('%Y.%m.%d')}",
                "doc_count": random.randint(100, 2000),
                "size_mb": random.randint(1, 100)
            }
        ],
        "total_size_mb": 0,
        "status": "success"
    }
    
    # Считаем общий размер
    for idx in data["indices"]:
        data["total_size_mb"] += idx["size_mb"]
    
    return data


def compress_data(data):
    """Симуляция сжатия данных"""
    compressed = {
        "size_before_mb": data["total_size_mb"],
        "size_after_mb": round(data["total_size_mb"] * 0.7, 2),
        "compression_ratio": "70%"
    }
    return compressed


def generate_checksum(data):
    """Генерация контрольной суммы (MD5)"""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_str.encode('utf-8')).hexdigest()


def save_report(report):
    """Сохранение отчёта в JSON файл"""
    filename = f"{REPORT_DIR}/backup_report_{report['timestamp'].replace(':', '-')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Отчёт сохранён: {filename}")
    return filename


def send_to_pushgateway(report):
    """Симуляция отправки метрик в Pushgateway"""
    print("\n📊 Отправка метрик в мониторинг (симуляция)...")
    
    metrics = f"""# TYPE backup_status gauge
backup_status{{job_name="{report['job_name']}"}} {1 if report['status'] == 'success' else 0}
# TYPE backup_size_bytes gauge
backup_size_bytes{{job_name="{report['job_name']}"}} {report['size_bytes']}
# TYPE backup_duration_seconds gauge
backup_duration_seconds{{job_name="{report['job_name']}"}} {report['duration_seconds']}
# TYPE backup_indices_count gauge
backup_indices_count{{job_name="{report['job_name']}"}} {report['indices_count']}
"""
    
    print("=== Метрики ===\n" + metrics)
    return metrics


def check_disk_space():
    """Проверка свободного места на диске"""
    import shutil
    total, used, free = shutil.disk_usage("/" if os.name != 'nt' else "C:/")
    
    free_gb = free // (2**30)
    total_gb = total // (2**30)
    used_gb = used // (2**30)
    
    print(f"\n💾 Информация о диске:")
    print(f"   Всего: {total_gb} GB")
    print(f"   Использовано: {used_gb} GB")
    print(f"   Свободно: {free_gb} GB")
    
    if free_gb < 1:
        print("   ⚠️  ВНИМАНИЕ: Очень мало свободного места!")
        return False
    else:
        print("   ✅ Места достаточно")
        return True


def simulate_backup_progress():
    """Симуляция прогресса бэкапа"""
    print("\n⏳ Выполнение бэкапа...")
    for i in range(0, 101, 10):
        time.sleep(0.2)
        print(f"   Прогресс: {i}%", end="\r")
    print("   Прогресс: 100% ✅")


def run_backup():
    """Основная функция тестового бэкапа"""
    print("=" * 60)
    print("   🗄️  ТЕСТОВЫЙ БЭКАП БЕЗ ELASTICSEARCH")
    print("=" * 60)
    
    start_time = time.time()
    status = "failed"
    size_bytes = 0
    indices_count = 0
    
    try:
        # 1. Проверка места на диске
        if not check_disk_space():
            print("⚠️  Продолжаем, но места мало...")
        
        # 2. Генерация случайных данных
        print("\n📦 Генерация тестовых данных...")
        data = generate_random_data()
        indices_count = len(data["indices"])
        size_bytes = data["total_size_mb"] * 1024 * 1024  # переводим в байты
        
        print(f"   Найдено индексов: {indices_count}")
        print(f"   Общий размер: {data['total_size_mb']} MB ({size_bytes / (1024*1024):.2f} MB)")
        
        # 3. Симуляция сжатия
        compressed = compress_data(data)
        print(f"   Сжатие: {compressed['size_before_mb']} MB → {compressed['size_after_mb']} MB")
        
        # 4. Симуляция прогресса
        simulate_backup_progress()
        
        # 5. Генерация контрольной суммы
        checksum = generate_checksum(data)
        print(f"   Контрольная сумма (MD5): {checksum}")
        
        status = "success"
        duration = int(time.time() - start_time)
        
        # 6. Формирование отчёта
        report = {
            "job_name": "elasticsearch_snapshot",
            "status": status,
            "size_bytes": size_bytes,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "checksum_md5": checksum,
            "indices_count": indices_count,
            "data": data,
            "compressed": compressed,
            "server": "localhost (тестовый)"
        }
        
        print("\n" + "=" * 60)
        print("   ✅ БЭКАП УСПЕШНО ЗАВЕРШЁН")
        print("=" * 60)
        
        # 7. Сохранение отчёта
        save_report(report)
        
        # 8. Отправка метрик (симуляция)
        send_to_pushgateway(report)
        
        # 9. Вывод отчёта на экран
        print("\n=== ОТЧЁТ О БЭКАПЕ ===")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
        return status
        
    except Exception as e:
        status = "failed"
        duration = int(time.time() - start_time)
        
        print(f"\n❌ Ошибка бэкапа: {e}")
        
        report = {
            "job_name": "elasticsearch_snapshot",
            "status": status,
            "size_bytes": 0,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "checksum_md5": hashlib.md5(str(e).encode()).hexdigest(),
            "error_message": str(e),
            "indices_count": 0
        }
        
        save_report(report)
        print("\n=== ОТЧЁТ ОБ ОШИБКЕ ===")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
        return status


def list_reports():
    """Просмотр сохранённых отчётов"""
    print("\n📂 Сохранённые отчёты:")
    if os.path.exists(REPORT_DIR):
        files = os.listdir(REPORT_DIR)
        if files:
            for f in sorted(files):
                print(f"   📄 {f}")
        else:
            print("   Нет сохранённых отчётов")
    else:
        print("   Папка для отчётов не создана")


if __name__ == "__main__":
    # Запуск бэкапа
    result = run_backup()
    
    # Просмотр сохранённых отчётов
    list_reports()
    
    print("\n" + "=" * 60)
    print(f"Результат: {'✅ УСПЕШНО' if result == 'success' else '❌ ОШИБКА'}")
    print("=" * 60)
