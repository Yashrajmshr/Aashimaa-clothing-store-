from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, SoftDeleteMixin

class Service(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True) # e.g. SRV-LHN-01
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True) # Alteration, Deep Cleaning, Finishing, Ironing, Tailoring
    division = Column(String(80), nullable=False, index=True) # AASHIMA Women's World vs AASHIMA Stitchers 'N' Drapers
    hsn_sac = Column(String(20), default="998822", nullable=False)
    description = Column(Text, nullable=True)
    turnaround_days = Column(Integer, default=3, nullable=False)
    requires_measurement = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    pricing_tiers = relationship("ServicePricing", back_populates="service", cascade="all, delete-orphan")
    booking_services = relationship("BookingService", back_populates="service")

class ServicePricing(Base, TimestampMixin):
    __tablename__ = "service_pricing"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    tier_name = Column(String(50), default="Standard", nullable=False) # Standard, Urgent / Express, Bridal Heirloom
    fabric_type = Column(String(80), nullable=True) # Silk, Velvet, Georgette, Wool, Cotton
    base_price = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), default=5.00, nullable=False) # 5%, 12%, 18%
    is_current = Column(Boolean, default=True, nullable=False)

    service = relationship("Service", back_populates="pricing_tiers")

class TailoringMeasurementTemplate(Base, TimestampMixin):
    __tablename__ = "tailoring_measurement_templates"

    id = Column(Integer, primary_key=True, index=True)
    garment_type = Column(String(80), unique=True, nullable=False, index=True) # COAT, PANT, SHIRT, KURTA_PAJAMA, LEHENGA, BLOUSE
    display_title = Column(String(100), nullable=False)
    unit_default = Column(String(10), default="INCH", nullable=False) # INCH or CM
    step_increment = Column(Numeric(4, 2), default=0.25, nullable=False) # 0.25 inch step
    anchor_fields = Column(Text, nullable=False) # JSON list of fields: ["length", "chest", "waist", "hip", "shoulder", "cross_back", "neck", "sleeve_length", "bicep", "wrist"]
    special_directives_placeholder = Column(Text, nullable=True)
    silhouette_icon = Column(String(50), nullable=True)
