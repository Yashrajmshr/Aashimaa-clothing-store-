from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.customer import CustomerResponse
from backend.app.schemas.garment import GarmentCreate, GarmentResponse

class OrderStatusHistoryResponse(BaseModel):
    id: int
    previous_status: Optional[str] = None
    new_status: str
    department: Optional[str] = None
    remarks: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    changed_by_name: Optional[str] = None

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    customer_id: int
    division: str # AASHIMA Women's World or AASHIMA Stitchers 'N' Drapers
    order_type: str = "Counter"
    delivery_due_date: datetime
    trial_due_date: Optional[datetime] = None
    is_urgent: bool = False
    urgent_reason: Optional[str] = None
    notes: Optional[str] = None
    garments: List[GarmentCreate]
    advance_payment_amount: Optional[Decimal] = Decimal("0.00")
    advance_payment_mode: Optional[str] = "UPI"
    advance_transaction_id: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    booking_number: str
    customer_id: int
    customer: Optional[CustomerResponse] = None
    division: str
    order_type: str
    current_status: str
    delivery_due_date: datetime
    trial_due_date: Optional[datetime] = None
    is_urgent: bool
    urgent_reason: Optional[str] = None
    total_amount: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    advance_paid: Decimal
    balance_due: Decimal
    payment_status: str
    notes: Optional[str] = None
    created_at: datetime
    garments: List[GarmentResponse] = []
    status_history: List[OrderStatusHistoryResponse] = []

    class Config:
        from_attributes = True
