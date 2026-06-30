"""
Репозиторий для работы с заказами
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import Order, OrderItem, OrderStatus
from app.exceptions import EntityNotFoundException, DeliveryCalculationException


class OrderRepository:
    """
    Репозиторий для работы с заказами в БД
    """
    
    def __init__(self, session: Session):
        """
        Инициализация репозитория
        
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def create(self, order_data: Dict[str, Any]) -> Order:
        """
        Создаёт заказ и связанные позиции из словаря
        
        Args:
            order_data: Словарь с данными заказа:
                - customer_name: str
                - delivery_address: str
                - total_amount: float
                - items: List[Dict] с полями product_name, quantity, price
                
        Returns:
            Созданный объект Order
        """
        # Извлекаем данные о позициях
        items_data = order_data.pop("items", [])
        
        # Создаём заказ
        order = Order(**order_data)
        self.session.add(order)
        self.session.flush()  # Получаем ID заказа
        
        # Создаём позиции
        for item_data in items_data:
            item = OrderItem(
                order_id=order.id,
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                price=item_data["price"]
            )
            self.session.add(item)
        
        # Сохраняем позиции в БД
        self.session.flush()
        
        # Пересчитываем общую сумму (теперь позиции в БД)
        order.total_amount = self._calculate_total_from_items(order.id)
        
        self.session.commit()
        self.session.refresh(order)
        return order

    def find_by_id(self, order_id: int) -> Optional[Order]:
        """
        Возвращает заказ по ID или None, если не найден
        
        Args:
            order_id: ID заказа
            
        Returns:
            Order или None
        """
        return self.session.query(Order).filter(Order.id == order_id).first()

    def find_all_by_status(self, status: str) -> List[Order]:
        """
        Возвращает список заказов с указанным статусом
        
        Args:
            status: Статус заказа
            
        Returns:
            Список заказов
        """
        return self.session.query(Order).filter(Order.status == status).all()

    def update_status(self, order_id: int, new_status: str) -> Order:
        """
        Обновляет статус заказа
        
        Args:
            order_id: ID заказа
            new_status: Новый статус
            
        Returns:
            Обновлённый заказ
            
        Raises:
            EntityNotFoundException: Если заказ не найден
        """
        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException(f"Order with id {order_id} not found")
        
        order.status = new_status
        self.session.commit()
        self.session.refresh(order)
        return order

    def delete(self, order_id: int) -> None:
        """
        Жёстко удаляет заказ и все его позиции из БД
        
        Args:
            order_id: ID заказа
        """
        order = self.find_by_id(order_id)
        if order:
            self.session.delete(order)
            self.session.commit()

    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """
        Возвращает заказы, созданные в указанном временном интервале
        
        Args:
            start_date: Начало интервала
            end_date: Конец интервала
            
        Returns:
            Список заказов
        """
        return self.session.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()

    def get_total_amount_for_order(self, order_id: int) -> float:
        """
        Вычисляет сумму всех позиций заказа
        
        Args:
            order_id: ID заказа
            
        Returns:
            Общая сумма
        """
        result = self.session.query(
            func.sum(OrderItem.quantity * OrderItem.price)
        ).filter(OrderItem.order_id == order_id).scalar()
        
        return result or 0.0

    def _calculate_total_from_items(self, order_id: int) -> float:
        """
        Вспомогательный метод для пересчёта суммы заказа
        """
        return self.get_total_amount_for_order(order_id)

    def calculate_delivery_cost(self, order_id: int) -> float:
        """
        Рассчитывает стоимость доставки через внешний API
        
        Args:
            order_id: ID заказа
            
        Returns:
            Стоимость доставки
            
        Raises:
            DeliveryCalculationException: При ошибке API
            EntityNotFoundException: Если заказ не найден
        """
        import httpx
        
        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException(f"Order with id {order_id} not found")
        
        # Вычисляем вес: количество * 0.5 кг
        total_weight = 0.0
        for item in order.items:
            total_weight += item.quantity * 0.5
        
        # Формируем запрос
        payload = {
            "address": order.delivery_address,
            "weight": total_weight
        }
        
        try:
            response = httpx.post(
                "https://api.delivery.com/calculate",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Проверяем наличие поля cost
            if "cost" not in data:
                raise DeliveryCalculationException(
                    f"Invalid response from delivery API: missing 'cost' field"
                )
            
            return data["cost"]
        except httpx.HTTPStatusError as e:
            raise DeliveryCalculationException(
                f"Delivery API error: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise DeliveryCalculationException(f"Delivery API request failed: {str(e)}")
        except (KeyError, ValueError) as e:
            raise DeliveryCalculationException(f"Invalid response from delivery API: {str(e)}")