import uuid
from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, func, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    master_id = Column(UUID(as_uuid=True), ForeignKey("master_products.id", ondelete="CASCADE"), nullable=False, index=True)
    target_price = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    notify_on_any_drop = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
