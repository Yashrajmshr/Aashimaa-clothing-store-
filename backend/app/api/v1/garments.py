import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.auth import User
from backend.app.models.booking import Garment, GarmentPhotograph, GarmentMeasurement
from backend.app.schemas.garment import GarmentResponse, GarmentPhotographResponse, GarmentMeasurementCreate, GarmentMeasurementResponse
from backend.app.services.workflow_engine import transition_garment_stage

router = APIRouter(prefix="/garments", tags=["Garment Management & Stage Updates"])

class StageTransitionPayload(BaseModel):
    new_stage: str # Alteration, Deep Cleaning, Finishing, Delivery Centre, Ready for Delivery, Out for Delivery, Delivered
    remarks: Optional[str] = None
    photo_url: Optional[str] = None
    department: Optional[str] = None
    assigned_karigar_name: Optional[str] = None

@router.get("/{garment_id}", response_model=GarmentResponse)
def get_garment(
    garment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garment = db.query(Garment).filter(Garment.id == garment_id, Garment.is_deleted == False).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")
    
    resp = GarmentResponse.model_validate(garment)
    if garment.qr_token:
        resp.qr_code_identifier = garment.qr_token.qr_code_identifier
        resp.secure_token = garment.qr_token.secure_token
    return resp

@router.post("/{garment_id}/transition", response_model=GarmentResponse)
def update_garment_stage(
    garment_id: int,
    payload: StageTransitionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garment = db.query(Garment).filter(Garment.id == garment_id, Garment.is_deleted == False).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    updated_garment, history = transition_garment_stage(
        db=db,
        garment=garment,
        new_stage=payload.new_stage,
        user_id=current_user.id,
        remarks=payload.remarks,
        photo_url=payload.photo_url,
        department=payload.department,
        assigned_karigar_name=payload.assigned_karigar_name
    )

    resp = GarmentResponse.model_validate(updated_garment)
    if updated_garment.qr_token:
        resp.qr_code_identifier = updated_garment.qr_token.qr_code_identifier
        resp.secure_token = updated_garment.qr_token.secure_token
    return resp

@router.post("/{garment_id}/photos", response_model=GarmentPhotographResponse)
def add_garment_photo(
    garment_id: int,
    photo_url: str,
    caption: Optional[str] = None,
    photo_stage: str = "In-Progress",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garment = db.query(Garment).filter(Garment.id == garment_id, Garment.is_deleted == False).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    photo = GarmentPhotograph(
        garment_id=garment.id,
        photo_url=photo_url,
        caption=caption,
        photo_stage=photo_stage,
        uploaded_by_user_id=current_user.id
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

@router.post("/{garment_id}/measurements", response_model=GarmentMeasurementResponse)
def save_garment_measurements(
    garment_id: int,
    payload: GarmentMeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    garment = db.query(Garment).filter(Garment.id == garment_id, Garment.is_deleted == False).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    meas = db.query(GarmentMeasurement).filter(GarmentMeasurement.garment_id == garment.id).first()
    if not meas:
        meas = GarmentMeasurement(garment_id=garment.id)
        db.add(meas)

    meas.template_garment_type = payload.template_garment_type
    meas.unit = payload.unit
    meas.measurements_json = json.dumps(payload.measurements)
    meas.karigar_directives = payload.karigar_directives
    meas.historical_baseline_reference = payload.historical_baseline_reference

    db.commit()
    db.refresh(meas)
    return meas
