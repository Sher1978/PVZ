import uuid
from sqlalchemy import Column, String, Text, BigInteger, Numeric, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Auction(Base):
    __tablename__ = "auctions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    photos = Column(JSON, default=list)  # list of Telegram file_ids (up to 5)
    starting_price = Column(Numeric(14, 2), nullable=False)
    current_price = Column(Numeric(14, 2), nullable=False)
    buyout_price = Column(Numeric(14, 2), nullable=False)
    min_bid_step = Column(Numeric(14, 2), default=50000.0)  # 50,000 VND
    status = Column(String(32), default="draft", index=True)  # draft, active, completed, cancelled
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True, index=True)
    
    winner_id = Column(BigInteger, nullable=True)  # Telegram ID of winner
    winning_bid = Column(Numeric(14, 2), nullable=True)
    winning_type = Column(String(32), nullable=True)  # 'bid' or 'buyout'
    winner_address = Column(Text, nullable=True)
    payment_status = Column(String(32), default="pending")  # pending, paid, expired
    payment_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Dict of {str(telegram_id): message_id} to track sent live post messages for updating in-place
    broadcast_messages = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    bids = relationship("AuctionBid", back_populates="auction", cascade="all, delete-orphan")

class AuctionBid(Base):
    __tablename__ = "auction_bids"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    auction_id = Column(String(36), ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)  # Telegram ID
    user_name = Column(String(128), nullable=True)
    username = Column(String(64), nullable=True)
    amount = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    auction = relationship("Auction", back_populates="bids")
