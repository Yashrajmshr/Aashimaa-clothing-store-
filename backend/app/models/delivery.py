from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class Delivery(Base, TimestampMixin):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    delivery_number = Column(String(50), unique=True, nullable=False, index=True) # DEL-2026-0042
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    delivery_type = Column(String(50), default="Store Pickup", nullable=False) # Store Pickup, Home Delivery, Atelier Chauffeur, Courier
    
    delivery_staff_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    courier_partner = Column(String(100), nullable=True) # BlueDart, Delhivery, In-House Rider
    tracking_reference = Column(String(100), nullable=True) # Waybill / Courier tracking #
    
    status = Column(String(50), default="Delivery Centre Staged", nullable=False, index=True) # Staged, Dispatched, Out for Delivery, Delivered, Failed Attempt, Rescheduled
    scheduled_date = Column(DateTime, nullable=False)
    actual_delivery_date = Column(DateTime, nullable=True)
    
    recipient_name = Column(String(120), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    proof_of_delivery_url = Column(String(255), nullable=True) # Signature or photo upload
    failure_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    booking = relationship("Booking", back_populates="deliveries")
    delivery_staff = relationship("User")
    updates = relationship("TransportationUpdate", back_populates="delivery", cascade="all, delete-orphan")

class TransportationUpdate(Base, TimestampMixin):
    __tablename__ = "transportation_updates"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False, index=True)
    status_update = Column(String(100), nullable=False) # "Dispatched from 581 Turab Nagar", "In Transit", "Out for Delivery"
    location = Column(String(150), nullable=False) # "Turab Nagar Hub", "Raj Nagar Sector 10"
    remarks = Column(Text, nullable=True)
    reported_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    delivery = relationship("Delivery", back_populates="updates")
