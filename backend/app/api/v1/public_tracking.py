from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.booking import Booking, Garment, OrderStatusHistory
from backend.app.models.customer import Customer
from backend.app.models.qr import GarmentQRToken
from backend.app.models.billing import Invoice
from backend.app.core.business_config import WorkflowStage

router = APIRouter(prefix="/public", tags=["Public Customer Tracking Portal"])

@router.get("/track")
def track_order_public(
    token: Optional[str] = Query(None, description="Secure QR token or QR identifier"),
    booking_number: Optional[str] = Query(None, description="Booking # e.g. ASH-8842"),
    phone: Optional[str] = Query(None, description="Customer 10-digit mobile number"),
    db: Session = Depends(get_db)
):
    """
    Public live tracking endpoint for AASHIMA Customer Portal.
    Read-only endpoint that returns live timeline, intake photos, karigar directives, and bill status.
    Supports lookup via secure QR token, flexible booking number (e.g. ASH-8843, 8843, #8843), or customer phone.
    """
    target_garment = None
    target_booking = None

    if token:
        clean_token = token.strip()
        qr_obj = db.query(GarmentQRToken).filter(
            (GarmentQRToken.secure_token == clean_token) |
            (GarmentQRToken.qr_code_identifier == clean_token) |
            (GarmentQRToken.qr_code_identifier == f"QR-{clean_token}")
        ).first()

        if not qr_obj:
            raise HTTPException(status_code=404, detail="Garment QR token not found or invalid.")

        target_garment = db.query(Garment).filter(Garment.id == qr_obj.garment_id).first()
        if target_garment:
            target_booking = target_garment.booking

    if not target_booking and booking_number:
        raw_num = booking_number.strip().replace("#", "").upper()
        candidates = [raw_num, f"ASH-{raw_num}", f"ASH{raw_num}"]
        target_booking = db.query(Booking).filter(
            Booking.booking_number.in_(candidates),
            Booking.is_deleted == False
        ).first()

        if not target_booking:
            target_booking = db.query(Booking).filter(
                Booking.booking_number.ilike(f"%{raw_num}%"),
                Booking.is_deleted == False
            ).first()

        if target_booking and target_booking.garments:
            target_garment = target_booking.garments[0]

    # If still not found and phone provided, lookup latest active booking for this phone
    if not target_booking and phone:
        clean_phone = "".join(filter(str.isdigit, phone))[-10:]
        if len(clean_phone) == 10:
            target_booking = (
                db.query(Booking)
                .join(Customer)
                .filter(
                    Customer.phone.endswith(clean_phone),
                    Booking.is_deleted == False
                )
                .order_by(Booking.created_at.desc())
                .first()
            )
            if target_booking and target_booking.garments:
                target_garment = target_booking.garments[0]

    if not target_booking:
        ref_text = booking_number or phone or token or "provided details"
        raise HTTPException(
            status_code=404,
            detail=f"No active atelier booking found for '{ref_text}'. Please check your booking number or contact Turab Nagar atelier at +91 98102 44321."
        )

    customer = target_booking.customer

    # Standard 5-stage timeline matching Google Stitch Public Portal design:
    # 1. Intake & Inspection
    # 2. Organic Fabric Care / Deep Cleaning
    # 3. Delicate Zari Polish & Steam Finishing
    # 4. Quality Inspection & Packaging (Active)
    # 5. Ready for Handover
    current_st = target_garment.current_stage if target_garment else target_booking.current_status

    # Map current internal stage to 5-stage display
    stage_progression = [
        {"title": "Intake & Inspection", "subtitle": "Barcode tag assigned. Verified client weave condition notes recorded.", "key": WorkflowStage.BOOKING_RECEIVED.value},
        {"title": "Organic Fabric Care", "subtitle": "Purified pH-balanced mild silk emulsion rinse and particulate removal.", "key": WorkflowStage.DEEP_CLEANING.value},
        {"title": "Delicate Zari Polish & Steam", "subtitle": f"Specialized temperature-regulated steam finishing. Karigar: {target_garment.karigar_name if target_garment else 'Atelier Master'}", "key": WorkflowStage.FINISHING.value},
        {"title": "Quality Inspection & Packaging", "subtitle": "Undergoing final micro-luster inspection & heirloom archival enclosure.", "key": WorkflowStage.DELIVERY_CENTRE.value},
        {"title": "Ready for Handover", "subtitle": "Turab Nagar Main Counter pickup with verified claim slip.", "key": WorkflowStage.READY_FOR_DELIVERY.value}
    ]

    # Calculate active status
    timeline_nodes = []
    found_active = False

    stage_order = [
        WorkflowStage.BOOKING_RECEIVED.value,
        WorkflowStage.ALTERATION.value,
        WorkflowStage.DEEP_CLEANING.value,
        WorkflowStage.FINISHING.value,
        WorkflowStage.DELIVERY_CENTRE.value,
        WorkflowStage.READY_FOR_DELIVERY.value,
        WorkflowStage.DELIVERED.value
    ]

    current_idx = stage_order.index(current_st) if current_st in stage_order else 0

    for idx, s in enumerate(stage_progression):
        s_idx = idx * 1.2
        if current_idx >= idx + 1:
            status_state = "Completed"
        elif current_idx == idx or (idx == 3 and current_idx in [3, 4]):
            status_state = "Active"
        else:
            status_state = "Upcoming"

        timeline_nodes.append({
            "stage_number": idx + 1,
            "title": s["title"],
            "description": s["subtitle"],
            "state": status_state,
            "timestamp": (target_booking.created_at + timedelta(days=idx)).strftime("%d %b • %I:%M %p") if status_state == "Completed" else "Upcoming"
        })

    # Visual proof photos (real uploaded intake snapshots only)
    intake_photos = []
    if target_garment and target_garment.photographs:
        for p in target_garment.photographs:
            intake_photos.append({
                "photo_url": p.photo_url,
                "caption": p.caption or "Intake condition snapshot",
                "stage": p.photo_stage
            })

    # Items breakdown
    items = []
    for g in target_booking.garments:
        srv_names = ", ".join([s.service_name for s in g.services]) or "Bespoke Garment Care"
        items.append({
            "garment_code": g.garment_code,
            "garment_name": g.garment_name,
            "article_tag": g.article_tag,
            "services": srv_names,
            "stage": g.current_stage,
            "price": float(g.item_price)
        })

    invoice = db.query(Invoice).filter(Invoice.booking_id == target_booking.id).first()
    invoice_url = f"/api/v1/billing/invoices/{invoice.id}/pdf" if invoice else None

    return {
        "booking_number": target_booking.booking_number,
        "division": target_booking.division,
        "shop_address": "581, Turab Nagar, Ghaziabad, UP, India",
        "customer_name": customer.full_name,
        "customer_unit": customer.unit_reference,
        "patron_tier": customer.patron_tier,
        "primary_garment": target_garment.garment_name if target_garment else "Bespoke Article",
        "current_status": current_st,
        "expected_delivery_date": target_booking.delivery_due_date.strftime("%d %b %Y, %I:%M %p"),
        "timeline": timeline_nodes,
        "intake_photos": intake_photos,
        "special_instructions": target_garment.special_instructions if target_garment else "",
        "items": items,
        "billing": {
            "total_amount": float(target_booking.net_amount),
            "advance_paid": float(target_booking.advance_paid),
            "balance_due": float(target_booking.balance_due),
            "payment_status": target_booking.payment_status,
            "invoice_pdf_url": invoice_url
        },
        "workshop_contact": {
            "phone": "+91 98102 44321",
            "whatsapp": "https://wa.me/919810244321?text=Inquiry%20regarding%20AASHIMA%20order%20" + target_booking.booking_number
        }
    }
