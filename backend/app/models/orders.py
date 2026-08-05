import uuid
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class OrderStatus(str, Enum):
    PENDING = "pending"              # Заказ создан, ожидает оплаты/подтверждения
    PURCHASED = "purchased"          # Товар выкуплен оператором ПВЗ
    IN_TRANSIT = "in_transit"        # В пути на ПВЗ
    READY_FOR_PICKUP = "ready"       # Прибыл в ПВЗ, готов к выдаче
    COMPLETED = "completed"          # Выдан клиенту
    CANCELLED = "cancelled"          # Отменен

class DeliveryMethod(str, Enum):
    BUY_FOR_ME = "buy_for_me"        # Вариант 2: Выкуп через ПВЗ (Основной)
    SELF_ORDER = "self_order"        # Вариант 1: Самостоятельный заказ на адрес ПВЗ

class PvzOrderModel(Base):
    __tablename__ = "pvz_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_telegram_id = Column(String(64), nullable=False, index=True)
    pvz_id = Column(String(64), nullable=False)
    pvz_name = Column(String(128), nullable=False)
    product_title = Column(String(512), nullable=False)
    product_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    platform = Column(String(32), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(8), default="VND")
    recipient_name = Column(String(128), nullable=False)
    recipient_phone = Column(String(32), nullable=False)
    delivery_method = Column(String(32), default=DeliveryMethod.BUY_FOR_ME.value)
    pickup_code = Column(String(16), nullable=False, index=True)
    tracking_number = Column(String(64), nullable=True)
    status = Column(String(32), default=OrderStatus.PENDING.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Schemas for API
class PvzPointSchema(BaseModel):
    id: str
    city: str
    name: str
    address_vn: str
    address_en: str
    working_hours: str
    phone: str
    is_active: bool = True

class CreatePvzOrderRequest(BaseModel):
    user_telegram_id: str = Field(..., description="Telegram ID пользователя")
    pvz_id: str = Field(..., description="ID выбранного ПВЗ")
    product_title: str
    product_url: str
    image_url: Optional[str] = None
    platform: str = "lazada"
    price: float
    currency: str = "VND"
    recipient_name: str
    recipient_phone: str
    delivery_method: DeliveryMethod = DeliveryMethod.BUY_FOR_ME

class RegisterSelfOrderRequest(BaseModel):
    user_telegram_id: str
    pvz_id: str
    tracking_number: str
    platform: str
    product_title: str

class PvzOrderResponse(BaseModel):
    id: str
    user_telegram_id: str
    pvz_id: str
    pvz_name: str
    product_title: str
    product_url: str
    image_url: Optional[str] = None
    platform: str
    price: float
    currency: str
    recipient_name: str
    recipient_phone: str
    delivery_method: str
    pickup_code: str
    tracking_number: Optional[str] = None
    status: str
    created_at: str
