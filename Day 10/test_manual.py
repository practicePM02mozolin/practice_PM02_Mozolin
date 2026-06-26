"""Ручная проверка работы валидатора (для отладки)"""
from fake_validator import FakeValidator
from datetime import datetime

# Создаём валидатор
validator = FakeValidator(chaos_mode=False)

print("=" * 50)
print("РУЧНАЯ ПРОВЕРКА ВАЛИДАТОРА")
print("=" * 50)

# === ТЕСТ 1: Валидный заказ ===
order1 = {
    "user_id": 1,
    "items": [
        {"product_id": 1, "quantity": 2, "price": 100}
    ],
    "total_amount": 200,
    "order_time": datetime(2026, 6, 16, 12, 0, 0),
    "is_new_user": False
}

result1 = validator.validate_order(order1)
print("\n✅ ТЕСТ 1: Валидный заказ")
print(f"   valid: {result1['valid']} (ожидается True)")
print(f"   risk_score: {result1['risk_score']} (ожидается 0.0)")
print(f"   reasons: {result1['reasons']} (ожидается [])")


# === ТЕСТ 2: Сумма превышает лимит ===
order2 = {
    "user_id": 1,
    "items": [
        {"product_id": 1, "quantity": 1, "price": 150000}
    ],
    "total_amount": 150000,
    "order_time": datetime(2026, 6, 16, 12, 0, 0),
    "is_new_user": False
}

result2 = validator.validate_order(order2)
print("\n❌ ТЕСТ 2: Сумма превышает лимит")
print(f"   valid: {result2['valid']} (ожидается False)")
print(f"   reasons: {result2['reasons']} (ожидается ['Сумма заказа превышает лимит'])")


# === ТЕСТ 3: Подозрительное количество + позднее время ===
order3 = {
    "user_id": 1,
    "items": [
        {"product_id": 1, "quantity": 15, "price": 100}
    ],
    "total_amount": 1500,
    "order_time": datetime(2026, 6, 16, 21, 30, 0),
    "is_new_user": False
}

result3 = validator.validate_order(order3)
print("\n⚠️ ТЕСТ 3: Подозрительное количество + позднее время")
print(f"   valid: {result3['valid']} (ожидается True)")
print(f"   risk_score: {result3['risk_score']} (ожидается 0.5)")
print(f"   reasons: {result3['reasons']}")


# === ТЕСТ 4: Время до 8:00 ===
order4 = {
    "user_id": 1,
    "items": [
        {"product_id": 1, "quantity": 1, "price": 100}
    ],
    "total_amount": 100,
    "order_time": datetime(2026, 6, 16, 7, 0, 0),
    "is_new_user": False
}

result4 = validator.validate_order(order4)
print("\n❌ ТЕСТ 4: Время до 8:00")
print(f"   valid: {result4['valid']} (ожидается False)")
print(f"   reasons: {result4['reasons']} (ожидается ['Заказ вне времени работы магазина'])")


# === ТЕСТ 5: Новый пользователь, превышен лимит ===
order5 = {
    "user_id": 2,
    "items": [
        {"product_id": 1, "quantity": 1, "price": 10000}
    ],
    "total_amount": 10000,
    "order_time": datetime(2026, 6, 16, 12, 0, 0),
    "is_new_user": True
}

result5 = validator.validate_order(order5)
print("\n❌ ТЕСТ 5: Новый пользователь, превышен лимит")
print(f"   valid: {result5['valid']} (ожидается False)")
print(f"   reasons: {result5['reasons']} (ожидается ['Превышен лимит для нового пользователя'])")

# === ИТОГ ===
print("\n" + "=" * 50)
print("РУЧНАЯ ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 50)
