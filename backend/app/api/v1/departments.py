from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.auth import User
from backend.app.models.booking import Garment, Booking
from backend.app.schemas.garment import GarmentResponse
from backend.app.core.business_config import WorkflowStage
from backend.app.core.business_config import UserRole

router = APIRouter(prefix="/departments", tags=["Department Work Queues & Karkhana Floor"])

@router.get("/alteration", response_model=List[GarmentResponse], dependencies=[Depends(require_roles([UserRole.STAFF, UserRole.MANAGER]))])
def get_alteration_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garments = db.query(Garment).filter(
        Garment.current_stage == WorkflowStage.ALTERATION.value,
        Garment.is_deleted == False
    ).order_by(Garment.created_at.asc()).all()
    return garments

@router.get("/deep-cleaning", response_model=List[GarmentResponse], dependencies=[Depends(require_roles([UserRole.STAFF, UserRole.MANAGER]))])
def get_deep_cleaning_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garments = db.query(Garment).filter(
        Garment.current_stage == WorkflowStage.DEEP_CLEANING.value,
        Garment.is_deleted == False
    ).order_by(Garment.created_at.asc()).all()
    return garments

@router.get("/finishing", response_model=List[GarmentResponse], dependencies=[Depends(require_roles([UserRole.STAFF, UserRole.MANAGER]))])
def get_finishing_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garments = db.query(Garment).filter(
        Garment.current_stage == WorkflowStage.FINISHING.value,
        Garment.is_deleted == False
    ).order_by(Garment.created_at.asc()).all()
    return garments

@router.get("/delivery-centre", response_model=List[GarmentResponse], dependencies=[Depends(require_roles([UserRole.STAFF, UserRole.MANAGER, UserRole.DELIVERY_STAFF]))])
def get_delivery_centre_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garments = db.query(Garment).filter(
        Garment.current_stage.in_([
            WorkflowStage.DELIVERY_CENTRE.value,
            WorkflowStage.READY_FOR_DELIVERY.value,
            WorkflowStage.OUT_FOR_DELIVERY.value
        ]),
        Garment.is_deleted == False
    ).order_by(Garment.created_at.asc()).all()
    return garments
