"""
Основной модуль FastAPI приложения
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.services import OrderService
from app.exceptions import EntityNotFoundException
from app.models import OrderResponse, ErrorResponse


app = FastAPI(title="Order Management API", version="1.0.0")


# ============ ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК ============

@app.exception_handler(EntityNotFoundException)
async def handle_entity_not_found(request, exc: EntityNotFoundException):
    """
    Глобальный обработчик исключения EntityNotFoundException
    
    Возвращает статус 404 с JSON сообщением об ошибке
    """
    return JSONResponse(
        status_code=404,
        content={"code": 404, "message": exc.message}
    )


# ============ ЗАВИСИМОСТИ ============

def get_order_service() -> OrderService:
    """
    Dependency Injection для OrderService
    """
    return OrderService()


# ============ ЭНДПОИНТЫ ============

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
) -> Dict[str, Any]:
    """
    Получение заказа по ID
    
    - **order_id**: ID заказа
    
    Возвращает данные заказа или ошибку 404, если заказ не найден
    """
    try:
        order = service.get_order(order_id)
        return order
    except EntityNotFoundException as e:
        # Исключение будет перехвачено глобальным обработчиком
        raise e


@app.get("/api/orders")
async def get_all_orders(
    service: OrderService = Depends(get_order_service)
) -> list:
    """
    Получение всех заказов
    """
    return service.get_all_orders()


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """
    Проверка работоспособности сервиса
    """
    return {"status": "ok"}