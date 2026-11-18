from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class QRTokenResponse(BaseModel):
    id: int
    garment_id: int
    qr_code_identifier: str
    secure_token: str
    public_tracking_url: str
    is_active: bool
    print_count: int
    last_printed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QRScanRequest(BaseModel):
    scanned_text: str # Could be raw URL or token or QR-ASH-8842-G01
    scan_context: str = "Stage Update"
    device_info: Optional[str] = None

class QRScanResponse(BaseModel):
    match_status: str # "100% Match", "Not Found", "Revoked"
    garment_id: int
    garment_code: str
    article_tag: Optional[str] = None
    garment_name: str
    category: str
    color: Optional[str] = None
    fabric_type: Optional[str] = None
    current_stage: str
    rack_location: Optional[str] = None
    booking_id: int
    booking_number: str
    customer_id: int
    customer_name: str
    customer_phone: str
    customer_unit: Optional[str] = None
    patron_tier: str
    special_instructions: Optional[str] = None
    defect_notes: Optional[str] = None
    photo_urls: List[str] = []

class QRPrintRequest(BaseModel):
    garment_ids: List[int]
    format: str = "80mm" # "58mm", "80mm", "A4"
