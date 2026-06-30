"""
Модуль с бизнес-логикой приложения
"""

from typing import Dict, Any, Optional
from app.exceptions import EntityNotFoundException


class OrderService:
    """
    Сервис для работы с заказами
    """
    
    def __init__(self):
        # Имитация базы данных
        self._orders = {
            1: {"id": 1, "total": 100.0, "status": "PAID"},
            2: {"id": 2, "total": 250.0, "status": "PENDING"},
            3: {"id": 3, "total": 75.0, "status": "SHIPPED"},
        }
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """
        Получение заказа по ID
        
        Args:
            order_id: ID заказа
            
        Returns:
            Dict с данными заказа
            
        Raises:
            EntityNotFoundException: если заказ не найден
        """
        order = self._orders.get(order_id)
        if order is None:
            raise EntityNotFoundException(f"Order with id {order_id} not found")
        return order
    
    def get_all_orders(self) -> list:
        """
        Получение всех заказов
        """
        return list(self._orders.values())