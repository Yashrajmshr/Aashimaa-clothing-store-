from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.auth import User
from backend.app.core.business_config import UserRole
from backend.app.models.delivery import Delivery, TransportationUpdate
from backend.app.schemas.delivery import (
    DeliveryCreate,
    DeliveryUpdate,
    DeliveryResponse,
    TransportationUpdateCreate,
    TransportationUpdateResponse
)

router = APIRouter(prefix="/deliveries", tags=["Transportation & Delivery Centre"])

@router.get("", response_model=List[DeliveryResponse], dependencies=[Depends(require_roles([UserRole.DELIVERY_STAFF, UserRole.MANAGER]))])
def list_deliveries(
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Delivery)
    if status:
        query = query.filter(Delivery.status == status)
    return query.order_by(Delivery.scheduled_date.asc()).offset(skip).limit(limit).all()

@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles([UserRole.MANAGER]))])
def create_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = db.query(Delivery).count() + 1
    del_num = f"DEL-{datetime.utcnow().year}-{count:04d}"

    delivery = Delivery(
        delivery_number=del_num,
        booking_id=payload.booking_id,
        delivery_type=payload.delivery_type,
        scheduled_date=payload.scheduled_date,
        recipient_name=payload.recipient_name,
        recipient_phone=payload.recipient_phone,
        delivery_staff_id=payload.delivery_staff_id,
        courier_partner=payload.courier_partner,
        tracking_reference=payload.tracking_reference,
        notes=payload.notes,
        status="Delivery Centre Staged"
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery

@router.post("/{delivery_id}/updates", response_model=TransportationUpdateResponse, dependencies=[Depends(require_roles([UserRole.DELIVERY_STAFF, UserRole.MANAGER]))])
def add_transport_update(
    delivery_id: int,
    payload: TransportationUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery record not found")

    upd = TransportationUpdate(
        delivery_id=delivery.id,
        status_update=payload.status_update,
        location=payload.location,
        remarks=payload.remarks,
        reported_by_user_id=current_user.id
    )
    delivery.status = payload.status_update
    db.add(upd)
    db.commit()
    db.refresh(upd)
    return upd

@router.put("/{delivery_id}", response_model=DeliveryResponse, dependencies=[Depends(require_roles([UserRole.DELIVERY_STAFF, UserRole.MANAGER]))])
def update_delivery(
    delivery_id: int,
    payload: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery record not found")

    if payload.status is not None:
        delivery.status = payload.status
    if payload.actual_delivery_date is not None:
        delivery.actual_delivery_date = payload.actual_delivery_date
    if payload.proof_of_delivery_url is not None:
        delivery.proof_of_delivery_url = payload.proof_of_delivery_url
    if payload.failure_reason is not None:
        delivery.failure_reason = payload.failure_reason
    if payload.notes is not None:
        delivery.notes = payload.notes

    db.commit()
    db.refresh(delivery)
    return delivery
