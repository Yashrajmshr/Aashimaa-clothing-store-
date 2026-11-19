from typing import Optional, List, Literal
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

class PaymentCreate(BaseModel):
    booking_id: int
    amount: Decimal = Field(..., gt=0)
    payment_type: Literal["Advance", "Partial", "Final", "Refund"] = "Partial"
    payment_mode: Literal["Cash", "UPI", "Card", "NetBanking", "Split"] = "UPI"
    transaction_id: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None

class PaymentReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    amount_paid: Decimal
    remaining_balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: int
    payment_reference: str
    booking_id: int
    customer_id: int
    amount: Decimal
    payment_type: str
    payment_mode: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    receipt: Optional[PaymentReceiptResponse] = None

    class Config:
        from_attributes = True

class InvoiceItemResponse(BaseModel):
    id: int
    item_description: str
    hsn_sac: str
    quantity: int
    unit_price: Decimal
    taxable_value: Decimal
    gst_rate: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    total_item_amount: Decimal

    class Config:
        from_attributes = True

class InvoiceCreate(BaseModel):
    booking_id: int
    invoice_type: Literal["GST", "Non-GST"] = "GST"
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    extra_charges: Decimal = Field(default=Decimal("0.00"), ge=0)

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    booking_id: int
    customer_id: int
    invoice_type: str
    division: str
    invoice_date: datetime
    subtotal_amount: Decimal
    discount_amount: Decimal
    extra_charges: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_tax_amount: Decimal
    grand_total: Decimal
    paid_amount: Decimal
    outstanding_balance: Decimal
    pdf_path: Optional[str] = None
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    category: str
    division: Optional[str] = None
    title: str
    amount: Decimal
    payment_mode: str = "Cash"
    paid_to: str
    notes: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    expense_number: str
    category: str
    division: Optional[str] = None
    title: str
    amount: Decimal
    payment_mode: str
    paid_to: str
    created_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class DaybookSummaryResponse(BaseModel):
    collected_today: Decimal
    pending_balance: Decimal
    cash_collected: Decimal
    upi_collected: Decimal
    card_collected: Decimal
    active_shift: str
    slips_billed_count: int
    avg_ticket_value: Decimal
    date_str: str
