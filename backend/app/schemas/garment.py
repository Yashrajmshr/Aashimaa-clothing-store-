from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class GarmentPhotographCreate(BaseModel):
    photo_url: str
    caption: Optional[str] = None
    photo_stage: str = "Intake"

class GarmentPhotographResponse(BaseModel):
    id: int
    photo_url: str
    caption: Optional[str] = None
    photo_stage: str
    created_at: datetime

    class Config:
        from_attributes = True

class GarmentMeasurementCreate(BaseModel):
    template_garment_type: str # COAT, PANT, SHIRT, KURTA_PAJAMA, LEHENGA_BLOUSE
    unit: str = "INCH" # INCH or CM
    measurements: Dict[str, float] # e.g. {"length": 29.5, "chest": 40.0}
    karigar_directives: Optional[str] = None
    historical_baseline_reference: Optional[str] = None

class GarmentMeasurementResponse(BaseModel):
    id: int
    garment_id: int
    template_garment_type: str
    unit: str
    measurements_json: str
    karigar_directives: Optional[str] = None
    historical_baseline_reference: Optional[str] = None

    class Config:
        from_attributes = True

class BookingServiceItemCreate(BaseModel):
    service_id: int

class BookingServiceItemResponse(BaseModel):
    id: int
    service_id: int
    service_name: str
    category: str
    price: Decimal
    gst_rate: Decimal
    gst_amount: Decimal
    total_service_price: Decimal

    class Config:
        from_attributes = True

class GarmentCreate(BaseModel):
    garment_name: str
    category: str
    fabric_type: Optional[str] = None
    color: Optional[str] = None
    quantity: int = 1
    rack_location: Optional[str] = None
    special_instructions: Optional[str] = None
    defect_notes: Optional[str] = None
    service_ids: List[int] = []
    measurement: Optional[GarmentMeasurementCreate] = None
    photo_urls: List[str] = []

class GarmentUpdate(BaseModel):
    garment_name: Optional[str] = None
    rack_location: Optional[str] = None
    karigar_name: Optional[str] = None
    special_instructions: Optional[str] = None
    defect_notes: Optional[str] = None

class GarmentResponse(BaseModel):
    id: int
    booking_id: int
    garment_code: str
    article_tag: Optional[str] = None
    garment_name: str
    category: str
    fabric_type: Optional[str] = None
    color: Optional[str] = None
    quantity: int
    current_stage: str
    rack_location: Optional[str] = None
    karigar_name: Optional[str] = None
    special_instructions: Optional[str] = None
    defect_notes: Optional[str] = None
    item_price: Decimal
    created_at: datetime
    services: List[BookingServiceItemResponse] = []
    photographs: List[GarmentPhotographResponse] = []
    measurements: Optional[GarmentMeasurementResponse] = None
    qr_code_identifier: Optional[str] = None
    secure_token: Optional[str] = None

    class Config:
        from_attributes = True
