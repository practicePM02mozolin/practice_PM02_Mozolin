"""Логирование"""

import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "booking_system",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Настройка логгера.
    
    Args:
        name: Имя логгера
        level: Уровень логирования
        log_file: Путь к файлу для логирования
        
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Убираем существующие обработчики
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый обработчик
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "booking_system") -> logging.Logger:
    """
    Получить логгер по имени.
    
    Args:
        name: Имя логгера
        
    Returns:
        Экземпляр логгера
    """
    return logging.getLogger(name)