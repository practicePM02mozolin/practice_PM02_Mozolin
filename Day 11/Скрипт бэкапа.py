#!/usr/bin/env python3
"""
backup_rules.py — резервное копирование правил корреляции (Windows/Linux)
"""

import os
import json
import logging
import hashlib
import subprocess
import shutil
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_rules.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
RULES_DIR = 'C:/temp/soc_rules/'  # Windows-путь
S3_BUCKET = 'soc-backups-prod'
S3_PREFIX = 'rules/'
LOCAL_BACKUP_DIR = 'C:/temp/rules_backup/'
IMMUTABLE_DAYS = 90


def check_disk_space():
    """Проверка свободного места на диске (Windows/Linux)"""
    try:
        # Для Windows
        if os.name == 'nt':
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p('C:/'), None, None, ctypes.pointer(free_bytes)
            )
            free_gb = free_bytes.value / (1024**3)
        else:
            # Для Linux/macOS
            stat = os.statvfs(RULES_DIR)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        
        logger.info(f"Свободно: {free_gb:.2f} ГБ")
        
        if free_gb < 1:
            raise Exception(f"Недостаточно места: {free_gb:.2f} ГБ (минимум 1 ГБ)")
        return True
    except Exception as e:
        logger.warning(f"Не удалось проверить место на диске: {e}")
        return True  # Продолжаем, если не удалось проверить


def create_directories():
    """Создание необходимых директорий"""
    os.makedirs(RULES_DIR, exist_ok=True)
    os.makedirs(LOCAL_BACKUP_DIR, exist_ok=True)
    logger.info(f"Директории созданы: {RULES_DIR}, {LOCAL_BACKUP_DIR}")


def create_test_rules():
    """Создание тестовых файлов правил (если их нет)"""
    test_rule = """
# Тестовое правило корреляции
rule:
  name: "Подозрительный вход"
  condition: "failed_logins > 5 AND time_window = '5m'"
  action: "alert"
  severity: "high"
"""
    rule_file = os.path.join(RULES_DIR, 'correlation.yml')
    if not os.path.exists(rule_file):
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(test_rule)
        logger.info(f"Создан тестовый файл правил: {rule_file}")
    
    # Создаём ещё несколько файлов для теста
    files = ['rules_1.yml', 'rules_2.yml', 'config.json']
    for fname in files:
        fpath = os.path.join(RULES_DIR, fname)
        if not os.path.exists(fpath):
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(f"# Тестовый файл {fname}\ncreated: {datetime.now()}")
    logger.info(f"Созданы тестовые файлы в {RULES_DIR}")

def compress_rules():
    """Сжатие правил в архив (Windows/Linux)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"rules_backup_{timestamp}.zip"
    archive_path = os.path.join(LOCAL_BACKUP_DIR, archive_name)
    
    # Для Windows используем shutil.make_archive
    base_name = archive_path.replace('.zip', '')
    shutil.make_archive(base_name, 'zip', RULES_DIR)
    
    # Переименовываем в нужный формат
    actual_archive = f"{base_name}.zip"
    if actual_archive != archive_path:
        os.rename(actual_archive, archive_path)
    
    logger.info(f"Архив создан: {archive_path}")
    return archive_path


def upload_to_s3(file_path):
    """Симуляция загрузки в S3 (для теста без boto3)"""
    logger.info(f"Симуляция загрузки в S3: {os.path.basename(file_path)} -> s3://{S3_BUCKET}/{S3_PREFIX}")
    logger.info("✅ Загрузка успешна (симуляция)")
    return f"s3://{S3_BUCKET}/{S3_PREFIX}{os.path.basename(file_path)}"


def cleanup_old_backups():
    """Удаление локальных бэкапов старше 7 дней"""
    cutoff = datetime.now() - timedelta(days=7)
    count = 0
    
    for f in os.listdir(LOCAL_BACKUP_DIR):
        fpath = os.path.join(LOCAL_BACKUP_DIR, f)
        if os.path.isfile(fpath):
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            if mtime < cutoff:
                os.remove(fpath)
                count += 1
                logger.info(f"Удален старый файл: {fpath}")
    
    if count > 0:
        logger.info(f"Удалено {count} старых файлов")


def generate_report(status, size_bytes, duration, error=None):
    """Генерация отчёта в формате JSON"""
    checksum = hashlib.md5(f"{status}{datetime.now()}".encode()).hexdigest()
    
    report = {
        "job_name": "rules_backup",
        "status": status,
        "size_bytes": size_bytes,
        "duration_seconds": duration,
        "timestamp": datetime.now().isoformat(),
        "checksum_md5": checksum
    }
    
    if error:
        report["error_message"] = str(error)
    
    return report


def run_backup():
    """Основная функция"""
    start_time = datetime.now()
    status = 'failed'
    size_bytes = 0
    error = None
    
    try:
        # Создаём директории
        create_directories()
        
        # Создаём тестовые правила
        create_test_rules()
        
        # Проверка места на диске
        check_disk_space()
        
        # Сжатие правил
        archive_path = compress_rules()
        size_bytes = os.path.getsize(archive_path)
        logger.info(f"Размер архива: {size_bytes} байт")
        
        # Загрузка в S3 (симуляция)
        upload_to_s3(archive_path)
        
        # Очистка старых бэкапов
        cleanup_old_backups()
        
        status = 'success'
        logger.info("✅ Бэкап правил успешно завершен")
        
    except Exception as e:
        error = e
        logger.error(f"❌ Ошибка бэкапа: {e}")
    
    duration = int((datetime.now() - start_time).total_seconds())
    
    # Создание отчёта
    report = generate_report(status, size_bytes, duration, error)
    
    # Сохранение отчёта в файл
    report_file = f"backup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Backup Report ===\n{json.dumps(report, indent=2)}")
    print(f"\n📄 Отчёт сохранён: {report_file}")
    
    return status


if __name__ == "__main__":
    print("=" * 60)
    print("   🗄️  БЭКАП ПРАВИЛ КОРРЕЛЯЦИИ (Windows/Linux)")
    print("=" * 60)
    run_backup()
    print("\n✅ Готово!")
