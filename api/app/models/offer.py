import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func, Numeric, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id = Column(UUID(as_uuid=True), ForeignKey("master_products.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(32), nullable=False)  # 'wb', 'ozon', 'yandex_market', 'aliexpress'
    external_sku = Column(String(128), nullable=False)
    title = Column(String(512), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=False, index=True)
    old_price = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="RUB")
    product_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    in_stock = Column(Boolean, default=True)
    rating = Column(Numeric(3, 2), nullable=True)
    reviews_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    master_product = relationship("MasterProduct", back_populates="offers")
    price_history = relationship("PriceHistory", back_populates="offer", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    offer = relationship("Offer", back_populates="price_history")
