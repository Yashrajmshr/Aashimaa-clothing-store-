from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class NotificationTemplate(Base, TimestampMixin):
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(80), unique=True, nullable=False, index=True)
    channel = Column(String(30), nullable=False) # SMS, WhatsApp, Both
    title = Column(String(150), nullable=False)
    template_body = Column(Text, nullable=False) # e.g. "Namaste {customer_name}, your garment {garment_name} is now Ready for Trial at AASHIMA, Turab Nagar."
    dlt_template_id = Column(String(50), nullable=True) # Indian TRAI / DLT regulatory template ID
    is_active = Column(Boolean, default=True, nullable=False)

class NotificationLog(Base, TimestampMixin):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_phone = Column(String(20), nullable=False, index=True)
    recipient_name = Column(String(120), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    
    event_type = Column(String(80), nullable=False, index=True)
    channel = Column(String(30), nullable=False) # SMS, WhatsApp
    provider = Column(String(50), default="mock", nullable=False) # mock, twilio, fast2sms, gupshup
    message_content = Column(Text, nullable=False)
    
    status = Column(String(30), default="Queued", nullable=False, index=True) # Queued, Sent, Delivered, Failed
    provider_message_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    delivered_at = Column(DateTime, nullable=True)

    customer = relationship("Customer")
    booking = relationship("Booking")
