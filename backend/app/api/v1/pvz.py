import random
import string
from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.models.orders import (
    PvzPointSchema,
    CreatePvzOrderRequest,
    RegisterSelfOrderRequest,
    PvzOrderResponse,
    OrderStatus,
    DeliveryMethod
)

router = APIRouter(prefix="/pvz", tags=["PVZ Pick-up Points & Delivery"])

# Active PVZ Pickup Points
ACTIVE_PVZ_POINTS: List[PvzPointSchema] = [
    PvzPointSchema(
        id="pvz_nhatrang_01",
        city="Nha Trang 🇻🇳",
        name="ПВЗ Нячанг (Центральный)",
        address_vn="123 Nguyễn Thiện Thuật, Phường Tân Lập, TP. Nha Trang, Khánh Hòa",
        address_en="123 Nguyen Thien Thuat, Tan Lap, Nha Trang, Khanh Hoa",
        working_hours="Ежедневно: 09:00 – 21:00",
        phone="+84 90 512 34 56",
        is_active=True
    ),
    PvzPointSchema(
        id="pvz_danang_01",
        city="Da Nang 🇻🇳",
        name="ПВЗ Дананг (Хайчау)",
        address_vn="45 Nguyễn Văn Linh, Phường Nam Dương, Quận Hải Châu, Đà Nẵng",
        address_en="45 Nguyen Van Linh, Nam Duong, Hai Chau, Da Nang",
        working_hours="Ежедневно: 09:00 – 20:00",
        phone="+84 90 678 90 12",
        is_active=True
    ),
    PvzPointSchema(
        id="pvz_saigon_01",
        city="Ho Chi Minh City 🇻🇳",
        name="ПВЗ Сайгон (Район 1)",
        address_vn="88 Lê Lợi, Phường Bến Thành, Quận 1, TP. Hồ Chí Minh",
        address_en="88 Le Loi, Ben Thanh, District 1, Ho Chi Minh City",
        working_hours="Ежедневно: 08:30 – 21:30",
        phone="+84 90 111 22 33",
        is_active=True
    )
]

# In-memory storage for demonstration & fast client interactions
MOCK_ORDERS_DB = [
    {
        "id": "ord_88412",
        "user_telegram_id": "demo_user",
        "pvz_id": "pvz_nhatrang_01",
        "pvz_name": "ПВЗ Нячанг (Центральный)",
        "product_title": "Беспроводные полноразмерные наушники Sony WH-1000XM5 Black",
        "product_url": "https://shopee.vn/product/12345",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80",
        "platform": "shopee",
        "price": 7490000.0,
        "currency": "VND",
        "recipient_name": "Игорь Филов",
        "recipient_phone": "+84 912 345 678",
        "delivery_method": DeliveryMethod.BUY_FOR_ME.value,
        "pickup_code": "PVZ-8841",
        "tracking_number": "SPX-VN-9081234",
        "status": OrderStatus.IN_TRANSIT.value,
        "created_at": "2026-08-05T14:30:00Z"
    }
]

def _generate_pickup_code() -> str:
    digits = ''.join(random.choices(string.digits, k=4))
    return f"PVZ-{digits}"

@router.get("/points", response_model=List[PvzPointSchema])
async def list_pvz_points():
    """Получить список всех активных пунктов выдачи заказов (ПВЗ)."""
    return ACTIVE_PVZ_POINTS

@router.post("/orders", response_model=PvzOrderResponse)
async def create_pvz_order(req: CreatePvzOrderRequest):
    """
    Вариант 2 (Основной): Создание заказа с выкупом через оператора ПВЗ.
    """
    pvz = next((p for p in ACTIVE_PVZ_POINTS if p.id == req.pvz_id), None)
    if not pvz:
        raise HTTPException(status_code=404, detail="Указанный ПВЗ не найден")

    order_id = f"ord_{random.randint(10000, 99999)}"
    pickup_code = _generate_pickup_code()
    
    order_data = {
        "id": order_id,
        "user_telegram_id": req.user_telegram_id,
        "pvz_id": pvz.id,
        "pvz_name": pvz.name,
        "product_title": req.product_title,
        "product_url": req.product_url,
        "image_url": req.image_url or "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&q=80",
        "platform": req.platform,
        "price": req.price,
        "currency": req.currency,
        "recipient_name": req.recipient_name,
        "recipient_phone": req.recipient_phone,
        "delivery_method": req.delivery_method.value,
        "pickup_code": pickup_code,
        "tracking_number": None,
        "status": OrderStatus.PENDING.value,
        "created_at": "2026-08-05T18:25:00Z"
    }
    MOCK_ORDERS_DB.insert(0, order_data)
    return PvzOrderResponse(**order_data)

@router.post("/track-external", response_model=PvzOrderResponse)
async def register_self_order(req: RegisterSelfOrderRequest):
    """
    Вариант 1 (Вспомогательный): Регистрация трек-номера самостоятельного заказа клиента.
    """
    pvz = next((p for p in ACTIVE_PVZ_POINTS if p.id == req.pvz_id), None)
    if not pvz:
        raise HTTPException(status_code=404, detail="ПВЗ не найден")

    order_id = f"self_{random.randint(10000, 99999)}"
    pickup_code = _generate_pickup_code()

    order_data = {
        "id": order_id,
        "user_telegram_id": req.user_telegram_id,
        "pvz_id": pvz.id,
        "pvz_name": pvz.name,
        "product_title": req.product_title,
        "product_url": "",
        "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&q=80",
        "platform": req.platform,
        "price": 0.0,
        "currency": "VND",
        "recipient_name": "Самостоятельный заказ",
        "recipient_phone": "",
        "delivery_method": DeliveryMethod.SELF_ORDER.value,
        "pickup_code": pickup_code,
        "tracking_number": req.tracking_number,
        "status": OrderStatus.IN_TRANSIT.value,
        "created_at": "2026-08-05T18:25:00Z"
    }
    MOCK_ORDERS_DB.insert(0, order_data)
    return PvzOrderResponse(**order_data)

@router.get("/orders", response_model=List[PvzOrderResponse])
async def get_user_orders(user_telegram_id: str = Query("demo_user")):
    """Получить список заказов пользователя в ПВЗ."""
    user_orders = [o for o in MOCK_ORDERS_DB if o["user_telegram_id"] == user_telegram_id or user_telegram_id == "demo_user"]
    return [PvzOrderResponse(**o) for o in user_orders]
