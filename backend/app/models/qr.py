from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class GarmentQRToken(Base, TimestampMixin):
    __tablename__ = "garment_qr_tokens"

    id = Column(Integer, primary_key=True, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    qr_code_identifier = Column(String(80), unique=True, nullable=False, index=True) # e.g. QR-ASH-8842-G01
    secure_token = Column(String(128), unique=True, nullable=False, index=True) # Unpredictable HMAC / UUIDv4 token
    public_tracking_url = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revocation_reason = Column(String(255), nullable=True)
    
    print_count = Column(Integer, default=0, nullable=False)
    last_printed_at = Column(DateTime, nullable=True)
    last_printed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    garment = relationship("Garment", back_populates="qr_token")
    scan_logs = relationship("QRScanHistory", back_populates="qr_token", cascade="all, delete-orphan")

class QRScanHistory(Base, TimestampMixin):
    __tablename__ = "qr_scan_history"

    id = Column(Integer, primary_key=True, index=True)
    qr_token_id = Column(Integer, ForeignKey("garment_qr_tokens.id", ondelete="CASCADE"), nullable=False, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="CASCADE"), nullable=False, index=True)
    scanned_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    scan_context = Column(String(50), default="Stage Update", nullable=False) # Stage Update, Rack Check, Customer Handover, Public Scan
    scan_result = Column(String(50), default="Success", nullable=False) # Success, Invalid Token, Expired
    device_info = Column(String(150), nullable=True)
    ip_address = Column(String(45), nullable=True)

    qr_token = relationship("GarmentQRToken", back_populates="scan_logs")
    garment = relationship("Garment")
    scanned_by = relationship("User")
