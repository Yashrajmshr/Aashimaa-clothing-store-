from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel

class ServicePricingBase(BaseModel):
    tier_name: str = "Standard"
    fabric_type: Optional[str] = None
    base_price: Decimal
    gst_rate: Decimal = Decimal("5.00")

class ServicePricingResponse(ServicePricingBase):
    id: int
    is_current: bool

    class Config:
        from_attributes = True

class ServiceBase(BaseModel):
    name: str
    category: str
    division: str
    hsn_sac: str = "998822"
    description: Optional[str] = None
    turnaround_days: int = 3
    requires_measurement: bool = False

class ServiceCreate(ServiceBase):
    base_price: Decimal
    gst_rate: Decimal = Decimal("5.00")

class ServiceResponse(ServiceBase):
    id: int
    code: str
    is_active: bool
    pricing_tiers: List[ServicePricingResponse] = []

    class Config:
        from_attributes = True

class MeasurementTemplateResponse(BaseModel):
    id: int
    garment_type: str
    display_title: str
    unit_default: str
    step_increment: Decimal
    anchor_fields: str
    special_directives_placeholder: Optional[str] = None
    silhouette_icon: Optional[str] = None

    class Config:
        from_attributes = True
