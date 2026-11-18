from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class TransportationUpdateCreate(BaseModel):
    status_update: str
    location: str
    remarks: Optional[str] = None

class TransportationUpdateResponse(BaseModel):
    id: int
    status_update: str
    location: str
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DeliveryCreate(BaseModel):
    booking_id: int
    delivery_type: str = "Store Pickup" # Store Pickup, Home Delivery, Atelier Chauffeur, Courier
    scheduled_date: datetime
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    delivery_staff_id: Optional[int] = None
    courier_partner: Optional[str] = None
    tracking_reference: Optional[str] = None
    notes: Optional[str] = None

class DeliveryUpdate(BaseModel):
    status: Optional[str] = None
    actual_delivery_date: Optional[datetime] = None
    proof_of_delivery_url: Optional[str] = None
    failure_reason: Optional[str] = None
    notes: Optional[str] = None

class DeliveryResponse(BaseModel):
    id: int
    delivery_number: str
    booking_id: int
    delivery_type: str
    status: str
    scheduled_date: datetime
    actual_delivery_date: Optional[datetime] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    courier_partner: Optional[str] = None
    tracking_reference: Optional[str] = None
    proof_of_delivery_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updates: List[TransportationUpdateResponse] = []

    class Config:
        from_attributes = True
