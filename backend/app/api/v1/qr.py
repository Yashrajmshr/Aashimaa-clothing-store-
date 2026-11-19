from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.auth import User
from backend.app.models.booking import Garment, Booking
from backend.app.models.customer import Customer
from backend.app.models.qr import GarmentQRToken, QRScanHistory
from backend.app.schemas.qr import QRScanRequest, QRScanResponse, QRPrintRequest
from backend.app.services.qr_service import generate_qr_data_uri, generate_thermal_slip_text
from backend.app.core.config import settings
from backend.app.core.business_config import UserRole

router = APIRouter(prefix="/qr", tags=["Unique QR Code System"])

@router.post("/scan", response_model=QRScanResponse, dependencies=[Depends(require_roles([UserRole.STAFF, UserRole.MANAGER, UserRole.DELIVERY_STAFF]))])
def scan_qr_code(
    payload: QRScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Staff QR scanning endpoint for fast floor stage transitions.
    Identifies garment by raw URL token or QR identifier.
    Logs scan history for audit trail.
    """
    raw = payload.scanned_text.strip()
    token_str = raw
    if "token=" in raw:
        token_str = raw.split("token=")[-1].split("&")[0]

    qr_token = db.query(GarmentQRToken).filter(
        (GarmentQRToken.secure_token == token_str) |
        (GarmentQRToken.qr_code_identifier == raw) |
        (GarmentQRToken.qr_code_identifier == f"QR-{raw}")
    ).first()

    if not qr_token or not qr_token.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not recognized or has been revoked."
        )

    garment = db.query(Garment).filter(Garment.id == qr_token.garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    booking = db.query(Booking).filter(Booking.id == garment.booking_id).first()
    customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()

    # Log Scan
    scan_log = QRScanHistory(
        qr_token_id=qr_token.id,
        garment_id=garment.id,
        scanned_by_user_id=current_user.id,
        scan_context=payload.scan_context,
        scan_result="Success",
        device_info=payload.device_info
    )
    db.add(scan_log)
    db.commit()

    photo_urls = [p.photo_url for p in garment.photographs]

    return QRScanResponse(
        match_status="100% Match",
        garment_id=garment.id,
        garment_code=garment.garment_code,
        article_tag=garment.article_tag,
        garment_name=garment.garment_name,
        category=garment.category,
        color=garment.color,
        fabric_type=garment.fabric_type,
        current_stage=garment.current_stage,
        rack_location=garment.rack_location,
        booking_id=booking.id,
        booking_number=booking.booking_number,
        customer_id=customer.id,
        customer_name=customer.full_name,
        customer_phone=customer.phone,
        customer_unit=customer.unit_reference,
        patron_tier=customer.patron_tier,
        special_instructions=garment.special_instructions,
        defect_notes=garment.defect_notes,
        photo_urls=photo_urls
    )

@router.post("/print-slips", dependencies=[Depends(require_roles([UserRole.STAFF, UserRole.MANAGER]))])
def generate_print_slips(
    payload: QRPrintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate printable thermal and barcode slips for single or multiple garments.
    Returns Base64 QR code data URIs and formatted monospace text for 58mm/80mm Bluetooth printers.
    """
    slips = []
    for g_id in payload.garment_ids:
        garment = db.query(Garment).filter(Garment.id == g_id).first()
        if not garment:
            continue

        booking = garment.booking
        customer = booking.customer
        qr_token = garment.qr_token

        if not qr_token:
            continue

        # Increment print count
        qr_token.print_count += 1
        qr_token.last_printed_at = datetime.utcnow()
        qr_token.last_printed_by_user_id = current_user.id

        qr_image_data_uri = generate_qr_data_uri(qr_token.public_tracking_url)
        service_names = [s.service_name for s in garment.services]
        due_str = booking.delivery_due_date.strftime("%d-%b-%Y %I:%M %p")

        slip_text = generate_thermal_slip_text(
            shop_name=settings.BUSINESS_NAME,
            address="581 Turab Nagar, Ghaziabad",
            phone=settings.SHOP_PHONE,
            booking_number=booking.booking_number,
            customer_name=customer.full_name,
            customer_phone=customer.phone,
            unit_reference=customer.unit_reference or "",
            garment_code=garment.garment_code,
            article_tag=garment.article_tag or "",
            garment_name=garment.garment_name,
            services=service_names,
            due_date_str=due_str,
            karigar_name=garment.karigar_name or "",
            rack_location=garment.rack_location or "Counter",
            advance_paid=f"{booking.advance_paid:.2f}",
            balance_due=f"{booking.balance_due:.2f}",
            width_mode=payload.format
        )

        slips.append({
            "garment_id": garment.id,
            "garment_code": garment.garment_code,
            "qr_code_identifier": qr_token.qr_code_identifier,
            "qr_image_data_uri": qr_image_data_uri,
            "public_tracking_url": qr_token.public_tracking_url,
            "thermal_text": slip_text,
            "format": payload.format,
            "customer_name": customer.full_name,
            "garment_name": garment.garment_name,
            "rack_location": garment.rack_location
        })

    db.commit()
    return {"slips": slips, "total": len(slips)}
