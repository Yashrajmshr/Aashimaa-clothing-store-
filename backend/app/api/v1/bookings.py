import json
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.auth import User
from backend.app.models.customer import Customer
from backend.app.models.service import Service
from backend.app.models.booking import (
    Booking,
    Garment,
    BookingService,
    GarmentMeasurement,
    GarmentPhotograph,
    OrderStatusHistory
)
from backend.app.models.qr import GarmentQRToken
from backend.app.models.billing import Payment, PaymentReceipt
from backend.app.schemas.booking import BookingCreate, BookingResponse
from backend.app.services.qr_service import generate_secure_token
from backend.app.services.billing_service import round_currency, generate_payment_reference, generate_receipt_number
from backend.app.core.business_config import WorkflowStage

router = APIRouter(prefix="/bookings", tags=["Booking Management"])

def generate_booking_number(db: Session) -> str:
    count = db.query(Booking).count() + 8843
    return f"ASH-{count}"

@router.get("", response_model=List[BookingResponse])
def list_bookings(
    search: Optional[str] = Query(None, description="Search by booking #, customer name or phone"),
    division: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_urgent: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Booking).filter(Booking.is_deleted == False)

    if search:
        search_fmt = f"%{search.strip().replace('#', '')}%"
        query = query.join(Customer).filter(
            or_(
                Booking.booking_number.ilike(search_fmt),
                Customer.full_name.ilike(search_fmt),
                Customer.phone.ilike(search_fmt)
            )
        )

    if division:
        query = query.filter(Booking.division == division)
    if status:
        query = query.filter(Booking.current_status == status)
    if is_urgent is not None:
        query = query.filter(Booking.is_urgent == is_urgent)

    bookings = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.is_deleted == False).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id, Customer.is_deleted == False).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not payload.garments:
        raise HTTPException(status_code=400, detail="At least one garment is required to create a booking")

    booking_num = generate_booking_number(db)
    
    total_amount = Decimal("0.00")
    total_tax = Decimal("0.00")

    # Pre-calculate prices
    garment_service_maps = []
    for g_idx, g_data in enumerate(payload.garments, 1):
        g_item_price = Decimal("0.00")
        services_to_attach = []
        for s_id in g_data.service_ids:
            service = db.query(Service).filter(Service.id == s_id).first()
            if service:
                price = service.pricing_tiers[0].base_price if service.pricing_tiers else Decimal("500.00")
                rate = service.pricing_tiers[0].gst_rate if service.pricing_tiers else Decimal("5.00")
                gst_amt = round_currency(price * (rate / Decimal("100.0")))
                total_srv_price = price + gst_amt
                
                g_item_price += price
                total_amount += price
                total_tax += gst_amt
                services_to_attach.append({
                    "service_id": service.id,
                    "service_name": service.name,
                    "category": service.category,
                    "price": price,
                    "gst_rate": rate,
                    "gst_amount": gst_amt,
                    "total_service_price": total_srv_price
                })
        garment_service_maps.append((g_data, g_item_price, services_to_attach))

    net_amount = total_amount + total_tax
    advance_amount = min(payload.advance_payment_amount or Decimal("0.00"), net_amount)
    balance_due = net_amount - advance_amount
    pay_status = "Paid" if balance_due <= Decimal("0.00") else ("Partial" if advance_amount > Decimal("0.00") else "Unpaid")

    # Create Booking
    booking = Booking(
        booking_number=booking_num,
        customer_id=customer.id,
        division=payload.division,
        order_type=payload.order_type,
        current_status=WorkflowStage.BOOKING_RECEIVED.value,
        delivery_due_date=payload.delivery_due_date,
        trial_due_date=payload.trial_due_date,
        is_urgent=payload.is_urgent,
        urgent_reason=payload.urgent_reason,
        total_amount=total_amount,
        discount_amount=Decimal("0.00"),
        tax_amount=total_tax,
        net_amount=net_amount,
        advance_paid=advance_amount,
        balance_due=balance_due,
        payment_status=pay_status,
        notes=payload.notes,
        created_by_user_id=current_user.id
    )
    db.add(booking)
    db.flush()

    # Create Garments, QR tokens, Measurements, Photos, BookingServices
    for idx, (g_data, g_price, srv_list) in enumerate(garment_service_maps, 1):
        g_code = f"{booking_num}-G{idx:02d}"
        art_tag = f"ART-{g_code[-4:]}"

        garment = Garment(
            booking_id=booking.id,
            garment_code=g_code,
            article_tag=art_tag,
            garment_name=g_data.garment_name,
            category=g_data.category,
            fabric_type=g_data.fabric_type,
            color=g_data.color,
            quantity=g_data.quantity,
            current_stage=WorkflowStage.BOOKING_RECEIVED.value,
            rack_location=g_data.rack_location or "Intake Counter",
            special_instructions=g_data.special_instructions,
            defect_notes=g_data.defect_notes,
            item_price=g_price
        )
        db.add(garment)
        db.flush()

        # Generate Cryptographic QR Token
        sec_token = generate_secure_token(g_code)
        qr_ident = f"QR-{g_code}"
        qr_obj = GarmentQRToken(
            garment_id=garment.id,
            qr_code_identifier=qr_ident,
            secure_token=sec_token,
            public_tracking_url=f"http://localhost:3000/track?token={sec_token}",
            is_active=True,
            print_count=0
        )
        db.add(qr_obj)

        # Attach Booking Services
        for s in srv_list:
            bs = BookingService(
                garment_id=garment.id,
                **s
            )
            db.add(bs)

        # Attach Measurements if provided
        if g_data.measurement:
            meas = GarmentMeasurement(
                garment_id=garment.id,
                template_garment_type=g_data.measurement.template_garment_type,
                unit=g_data.measurement.unit,
                measurements_json=json.dumps(g_data.measurement.measurements),
                karigar_directives=g_data.measurement.karigar_directives,
                historical_baseline_reference=g_data.measurement.historical_baseline_reference
            )
            db.add(meas)

        # Attach Photos if provided
        for p_url in g_data.photo_urls:
            photo = GarmentPhotograph(
                garment_id=garment.id,
                photo_url=p_url,
                caption="Intake documentation photo",
                photo_stage="Intake",
                uploaded_by_user_id=current_user.id
            )
            db.add(photo)

        # Initial Status History
        history = OrderStatusHistory(
            booking_id=booking.id,
            garment_id=garment.id,
            previous_status=None,
            new_status=WorkflowStage.BOOKING_RECEIVED.value,
            department="INTAKE",
            changed_by_user_id=current_user.id,
            remarks="Garment booked and tagged at 581 Turab Nagar counter."
        )
        db.add(history)

    # If advance payment collected, record Payment and Receipt
    if advance_amount > Decimal("0.00"):
        pay_ref = generate_payment_reference(db)
        rec_num = generate_receipt_number(db)
        payment = Payment(
            payment_reference=pay_ref,
            booking_id=booking.id,
            customer_id=customer.id,
            amount=advance_amount,
            payment_type="Advance",
            payment_mode=payload.advance_payment_mode or "UPI",
            transaction_id=payload.advance_transaction_id,
            notes="Booking advance collected",
            collected_by_user_id=current_user.id
        )
        db.add(payment)
        db.flush()

        receipt = PaymentReceipt(
            receipt_number=rec_num,
            payment_id=payment.id,
            amount_paid=advance_amount,
            remaining_balance=balance_due
        )
        db.add(receipt)

    # Update Customer metrics
    customer.total_orders += 1
    customer.lifetime_spend += net_amount
    customer.outstanding_dues += balance_due

    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft-delete a production order from the database.
    Hides the order from active queues and adjusts customer lifetime metrics.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.is_deleted == False).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking order not found")

    # Soft delete booking record
    booking.soft_delete()

    # Soft delete associated garments
    for garment in booking.garments:
        garment.soft_delete()

    # Recalculate customer metrics if customer exists
    if booking.customer:
        if booking.customer.total_orders > 0:
            booking.customer.total_orders -= 1
        booking.customer.lifetime_spend = max(Decimal("0.00"), booking.customer.lifetime_spend - booking.net_amount)
        booking.customer.outstanding_dues = max(Decimal("0.00"), booking.customer.outstanding_dues - booking.balance_due)

    db.commit()
    return {
        "status": "success",
        "message": f"Order #{booking.booking_number} deleted successfully",
        "booking_id": booking_id
    }
