# booking-system/conftest.py
import sys
from pathlib import Path

# Добавляем корневую директорию в sys.path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))