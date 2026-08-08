from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=False)
    language_code = Column(String(8), default="ru")
    is_premium = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String(32), default="user", index=True)  # superadmin, admin, staff, user
    is_auction_subscribed = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
