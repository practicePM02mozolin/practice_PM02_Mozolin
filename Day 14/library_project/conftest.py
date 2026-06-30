# conftest.py
import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print(f"✅ PYTHONPATH установлен: {root_dir}")