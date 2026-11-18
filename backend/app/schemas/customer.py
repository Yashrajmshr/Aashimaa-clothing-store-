from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class CustomerAddressBase(BaseModel):
    address_type: str = "Home"
    address_line1: str
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: str = "Ghaziabad"
    state: str = "Uttar Pradesh"
    pincode: str = "201001"
    is_default: bool = True

class CustomerAddressCreate(CustomerAddressBase):
    pass

class CustomerAddressResponse(CustomerAddressBase):
    id: int
    customer_id: int

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    patron_tier: str = "Standard"
    unit_reference: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    address: Optional[CustomerAddressCreate] = None

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    patron_tier: Optional[str] = None
    unit_reference: Optional[str] = None
    notes: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    customer_code: str
    total_orders: int
    lifetime_spend: Decimal
    outstanding_dues: Decimal
    created_at: datetime
    addresses: List[CustomerAddressResponse] = []

    class Config:
        from_attributes = True
