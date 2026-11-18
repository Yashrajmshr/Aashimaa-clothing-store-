from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, SoftDeleteMixin

class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. CUST-0941
    full_name = Column(String(120), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(120), nullable=True, index=True)
    patron_tier = Column(String(30), default="Standard", nullable=False) # Standard, Silver, Gold Patron, Platinum Bridal
    unit_reference = Column(String(50), nullable=True) # e.g., Unit #B-14 from Stitch design
    notes = Column(Text, nullable=True)
    total_orders = Column(Integer, default=0, nullable=False)
    lifetime_spend = Column(Numeric(12, 2), default=0.00, nullable=False)
    outstanding_dues = Column(Numeric(12, 2), default=0.00, nullable=False)
    
    # OTP Authentication Fields
    last_otp = Column(String(10), nullable=True)
    otp_generated_at = Column(DateTime, nullable=True)
    otp_attempts = Column(Integer, default=0, nullable=False)

    addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="customer")
    feedback = relationship("Feedback", back_populates="customer")
    support_tickets = relationship("SupportTicket", back_populates="customer")

class CustomerAddress(Base, TimestampMixin):
    __tablename__ = "customer_addresses"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    address_type = Column(String(30), default="Home", nullable=False) # Home, Boutique, Atelier, Studio
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    landmark = Column(String(150), nullable=True)
    city = Column(String(100), default="Ghaziabad", nullable=False)
    state = Column(String(100), default="Uttar Pradesh", nullable=False)
    pincode = Column(String(10), nullable=False)
    is_default = Column(Boolean, default=True, nullable=False)

    customer = relationship("Customer", back_populates="addresses")

class Feedback(Base, TimestampMixin):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True, index=True)
    rating = Column(Integer, nullable=False) # 1 to 5 stars
    fitting_satisfaction = Column(String(50), nullable=True) # Perfect, Minor Tight, Loose
    fabric_finish_satisfaction = Column(String(50), nullable=True) # Exquisite, Good, Satisfactory
    comments = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)

    customer = relationship("Customer", back_populates="feedback")
    booking = relationship("Booking", back_populates="feedbacks")

class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True) # e.g., TKT-2026-001
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    subject = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False) # Fitting Alteration, Delivery Delay, Billing Inquiry, Care Question
    priority = Column(String(20), default="Normal", nullable=False) # Low, Normal, High, Urgent
    status = Column(String(30), default="Open", nullable=False) # Open, In Progress, Resolved, Closed
    description = Column(Text, nullable=False)
    resolution_notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="support_tickets")
    booking = relationship("Booking")
