import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.service import Service, ServicePricing, TailoringMeasurementTemplate
from backend.app.models.booking import GarmentMeasurement, Garment, Booking
from backend.app.models.customer import Customer
from backend.app.models.auth import User
from backend.app.schemas.service import ServiceResponse, MeasurementTemplateResponse

router = APIRouter(prefix="/services", tags=["Services & Measurement Templates"])

@router.get("", response_model=List[ServiceResponse])
def list_services(
    division: Optional[str] = Query(None, description="AASHIMA Women's World or AASHIMA Stitchers 'N' Drapers"),
    category: Optional[str] = Query(None),
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Service).filter(Service.is_active == is_active)
    if division:
        query = query.filter(Service.division == division)
    if category:
        query = query.filter(Service.category == category)
    return query.order_by(Service.name.asc()).all()

@router.get("/templates/measurement", response_model=List[MeasurementTemplateResponse])
def list_measurement_templates(
    garment_type: Optional[str] = Query(None),
    gender: Optional[str] = Query(None, description="Men or Women"),
    db: Session = Depends(get_db)
):
    query = db.query(TailoringMeasurementTemplate)
    if garment_type:
        query = query.filter(TailoringMeasurementTemplate.garment_type == garment_type.upper())
    if gender:
        query = query.filter(TailoringMeasurementTemplate.silhouette_icon.ilike(gender.strip()))
    return query.order_by(TailoringMeasurementTemplate.silhouette_icon.asc(), TailoringMeasurementTemplate.display_title.asc()).all()

@router.get("/measurements/records")
def list_recorded_measurements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns real recorded tailoring measurements from active bookings."""
    records = (
        db.query(GarmentMeasurement, Garment, Booking, Customer)
        .join(Garment, GarmentMeasurement.garment_id == Garment.id)
        .join(Booking, Garment.booking_id == Booking.id)
        .join(Customer, Booking.customer_id == Customer.id)
        .filter(Booking.is_deleted == False, Garment.is_deleted == False)
        .order_by(GarmentMeasurement.created_at.desc())
        .limit(100)
        .all()
    )
    results = []
    for meas, garment, booking, customer in records:
        try:
            m_dict = json.loads(meas.measurements_json) if meas.measurements_json else {}
        except Exception:
            m_dict = {}
        results.append({
            "id": meas.id,
            "booking_number": booking.booking_number,
            "customer_name": customer.full_name,
            "customer_phone": customer.phone,
            "garment_name": garment.garment_name,
            "garment_type": meas.template_garment_type,
            "unit": meas.unit,
            "measurements": m_dict,
            "karigar_directives": meas.karigar_directives,
            "created_at": meas.created_at.isoformat()
        })
    return results
