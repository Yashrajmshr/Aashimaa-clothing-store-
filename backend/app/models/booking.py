from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, SoftDeleteMixin

class Booking(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_number = Column(String(50), unique=True, nullable=False, index=True) # e.g. ASH-8842
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    division = Column(String(80), nullable=False, index=True) # AASHIMA Women's World or AASHIMA Stitchers 'N' Drapers
    
    order_type = Column(String(50), default="Counter", nullable=False) # Counter, Home Pickup, Bridal Atelier
    current_status = Column(String(50), default="Booking Received", nullable=False, index=True)
    delivery_due_date = Column(DateTime, nullable=False, index=True)
    trial_due_date = Column(DateTime, nullable=True)
    is_urgent = Column(Boolean, default=False, nullable=False, index=True)
    urgent_reason = Column(String(200), nullable=True) # e.g. Bridal Handover, Karva Chauth

    total_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    net_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    advance_paid = Column(Numeric(12, 2), default=0.00, nullable=False)
    balance_due = Column(Numeric(12, 2), default=0.00, nullable=False)
    payment_status = Column(String(30), default="Unpaid", nullable=False, index=True) # Unpaid, Partial, Paid

    notes = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    customer = relationship("Customer", back_populates="bookings")
    garments = relationship("Garment", back_populates="booking", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="booking")
    invoices = relationship("Invoice", back_populates="booking")
    deliveries = relationship("Delivery", back_populates="booking")
    status_history = relationship("OrderStatusHistory", back_populates="booking", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="booking")

class Garment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "garments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    garment_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. ASH-8842-G01
    article_tag = Column(String(50), nullable=True) # e.g. LHN-0941
    garment_name = Column(String(150), nullable=False) # e.g. Heavy Bridal Lehenga, Pure Kanjeevaram Saree
    category = Column(String(50), nullable=False) # Lehenga, Saree, Blouse, Coat, Pant, Sherwani
    fabric_type = Column(String(80), nullable=True) # Pure Silk, Velvet, Georgette, Brocade
    color = Column(String(50), nullable=True) # Crimson Magenta, Royal Navy, Gold Zari
    quantity = Column(Integer, default=1, nullable=False)
    
    current_stage = Column(String(50), default="Booking Received", nullable=False, index=True)
    rack_location = Column(String(50), nullable=True) # e.g. Rack #B-14, Station #2
    karigar_name = Column(String(100), nullable=True) # e.g. Master Iqbal, Master Ramesh
    karigar_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    special_instructions = Column(Text, nullable=True) # Karigar directives
    defect_notes = Column(Text, nullable=True) # Verified client gold weave condition notes
    item_price = Column(Numeric(10, 2), default=0.00, nullable=False)

    booking = relationship("Booking", back_populates="garments")
    services = relationship("BookingService", back_populates="garment", cascade="all, delete-orphan")
    photographs = relationship("GarmentPhotograph", back_populates="garment", cascade="all, delete-orphan")
    measurements = relationship("GarmentMeasurement", back_populates="garment", uselist=False, cascade="all, delete-orphan")
    qr_token = relationship("GarmentQRToken", back_populates="garment", uselist=False, cascade="all, delete-orphan")
    department_assignments = relationship("DepartmentAssignment", back_populates="garment", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="garment")

    @property
    def qr_code_identifier(self):
        return self.qr_token.qr_code_identifier if self.qr_token else None

    @property
    def secure_token(self):
        return self.qr_token.secure_token if self.qr_token else None

class GarmentPhotograph(Base, TimestampMixin):
    __tablename__ = "garment_photographs"

    id = Column(Integer, primary_key=True, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="CASCADE"), nullable=False, index=True)
    photo_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    caption = Column(String(200), nullable=True) # e.g. "Pallu Border Check", "Intake inspection"
    photo_stage = Column(String(50), default="Intake", nullable=False) # Intake, In-Progress, QC Passed, Defect
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    garment = relationship("Garment", back_populates="photographs")

class GarmentMeasurement(Base, TimestampMixin):
    __tablename__ = "garment_measurements"

    id = Column(Integer, primary_key=True, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    template_garment_type = Column(String(50), nullable=False) # COAT, PANT, SHIRT, KURTA_PAJAMA, LEHENGA, BLOUSE
    unit = Column(String(10), default="INCH", nullable=False) # INCH or CM
    
    # Store numeric measurements as JSON for high flex + schema validation
    # Keys: length, chest, waist, hip, shoulder, cross_back, neck, sleeve_length, bicep, wrist, etc.
    measurements_json = Column(Text, nullable=False)
    karigar_directives = Column(Text, nullable=True)
    historical_baseline_reference = Column(String(100), nullable=True) # e.g. "May 2023 fitting archive"

    garment = relationship("Garment", back_populates="measurements")

class BookingService(Base, TimestampMixin):
    __tablename__ = "booking_services"

    id = Column(Integer, primary_key=True, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="RESTRICT"), nullable=False, index=True)
    service_name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), default=5.00, nullable=False)
    gst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_service_price = Column(Numeric(10, 2), nullable=False)

    garment = relationship("Garment", back_populates="services")
    service = relationship("Service", back_populates="booking_services")

class DepartmentAssignment(Base, TimestampMixin):
    __tablename__ = "department_assignments"

    id = Column(Integer, primary_key=True, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="CASCADE"), nullable=False, index=True)
    department = Column(String(50), nullable=False, index=True) # ALTERATION, DEEP_CLEAN, FINISHING, QC_PACKAGING, DELIVERY_CENTRE
    assigned_karigar_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), default="Pending", nullable=False) # Pending, In Progress, Completed, Skipped
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    garment = relationship("Garment", back_populates="department_assignments")
    karigar = relationship("User")

class WorkflowStageConfig(Base, TimestampMixin):
    __tablename__ = "workflow_stage_configs"

    id = Column(Integer, primary_key=True, index=True)
    service_category = Column(String(50), nullable=False, index=True) # Tailoring, Deep Cleaning, Alteration, Finishing
    stage_name = Column(String(50), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    estimated_hours = Column(Integer, default=24, nullable=False)
    department = Column(String(50), nullable=False)

class OrderStatusHistory(Base, TimestampMixin):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    garment_id = Column(Integer, ForeignKey("garments.id", ondelete="CASCADE"), nullable=True, index=True)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False, index=True)
    department = Column(String(50), nullable=True)
    changed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)

    booking = relationship("Booking", back_populates="status_history")
    garment = relationship("Garment", back_populates="status_history")
    changed_by = relationship("User")
