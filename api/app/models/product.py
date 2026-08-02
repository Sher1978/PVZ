import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)

class MasterProduct(Base):
    __tablename__ = "master_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512), nullable=False)
    brand = Column(String(128), index=True, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    main_image_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    offers = relationship("Offer", back_populates="master_product", cascade="all, delete-orphan")
