from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, SoftDeleteMixin

class GSTConfiguration(Base, TimestampMixin):
    __tablename__ = "gst_configurations"

    id = Column(Integer, primary_key=True, index=True)
    legal_name = Column(String(150), nullable=False)
    trade_name = Column(String(150), nullable=False)
    gstin = Column(String(20), unique=True, nullable=False, index=True)
    state_code = Column(String(5), default="09", nullable=False) # 09 for Uttar Pradesh
    state_name = Column(String(50), default="Uttar Pradesh", nullable=False)
    address = Column(String(255), nullable=False)
    is_composition = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Invoice(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True) # e.g. ASH-INV-2026-0042
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    invoice_type = Column(String(20), default="GST", nullable=False) # GST, Non-GST
    division = Column(String(80), nullable=False)
    invoice_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    subtotal_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    extra_charges = Column(Numeric(10, 2), default=0.00, nullable=False)
    taxable_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    
    cgst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    sgst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    igst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_tax_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    grand_total = Column(Numeric(12, 2), default=0.00, nullable=False)
    round_off = Column(Numeric(6, 2), default=0.00, nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    outstanding_balance = Column(Numeric(12, 2), default=0.00, nullable=False)
    
    pdf_path = Column(String(255), nullable=True)
    generated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    booking = relationship("Booking", back_populates="invoices")
    customer = relationship("Customer")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    receipts = relationship("PaymentReceipt", back_populates="invoice")

class InvoiceItem(Base, TimestampMixin):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="SET NULL"), nullable=True)
    
    item_description = Column(String(255), nullable=False)
    hsn_sac = Column(String(20), default="998822", nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    item_discount = Column(Numeric(10, 2), default=0.00, nullable=False)
    taxable_value = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), default=5.00, nullable=False)
    cgst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    sgst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_item_amount = Column(Numeric(10, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    garment = relationship("Garment")

class Payment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_reference = Column(String(50), unique=True, nullable=False, index=True) # PAY-2026-0089
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    amount = Column(Numeric(12, 2), nullable=False)
    payment_type = Column(String(30), default="Advance", nullable=False) # Advance, Partial, Final, Refund
    payment_mode = Column(String(30), nullable=False) # Cash, UPI, Card, NetBanking
    transaction_id = Column(String(100), nullable=True) # UPI UTR / Card Auth Code
    notes = Column(Text, nullable=True)
    collected_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    booking = relationship("Booking", back_populates="payments")
    customer = relationship("Customer")
    receipt = relationship("PaymentReceipt", back_populates="payment", uselist=False, cascade="all, delete-orphan")

class PaymentReceipt(Base, TimestampMixin):
    __tablename__ = "payment_receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False, index=True) # REC-2026-0089
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True)
    
    amount_paid = Column(Numeric(12, 2), nullable=False)
    remaining_balance = Column(Numeric(12, 2), nullable=False)
    pdf_path = Column(String(255), nullable=True)

    payment = relationship("Payment", back_populates="receipt")
    invoice = relationship("Invoice", back_populates="receipts")

class Expense(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    expense_number = Column(String(50), unique=True, nullable=False, index=True) # EXP-2026-001
    category = Column(String(50), nullable=False, index=True) # Threads & Trims, Chemicals & Detergents, Packaging, Workshop Electricity, Karigar Advance, Equipment Maintenance
    division = Column(String(80), nullable=True)
    title = Column(String(150), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_mode = Column(String(30), default="Cash", nullable=False)
    paid_to = Column(String(150), nullable=False)
    receipt_voucher_url = Column(String(255), nullable=True)
    approved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
