from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.core.business_config import WorkflowStage, DepartmentCode
from backend.app.models.booking import Booking, Garment, OrderStatusHistory, DepartmentAssignment

VALID_STAGE_TRANSITIONS = {
    WorkflowStage.BOOKING_RECEIVED: [
        WorkflowStage.ALTERATION,
        WorkflowStage.DEEP_CLEANING,
        WorkflowStage.FINISHING,
        WorkflowStage.DELIVERY_CENTRE,
        WorkflowStage.ON_HOLD,
        WorkflowStage.CANCELLED
    ],
    WorkflowStage.ALTERATION: [
        WorkflowStage.DEEP_CLEANING,
        WorkflowStage.FINISHING,
        WorkflowStage.READY_FOR_DELIVERY,
        WorkflowStage.ON_HOLD
    ],
    WorkflowStage.DEEP_CLEANING: [
        WorkflowStage.FINISHING,
        WorkflowStage.DELIVERY_CENTRE,
        WorkflowStage.READY_FOR_DELIVERY,
        WorkflowStage.ON_HOLD
    ],
    WorkflowStage.FINISHING: [
        WorkflowStage.DELIVERY_CENTRE,
        WorkflowStage.READY_FOR_DELIVERY,
        WorkflowStage.ON_HOLD
    ],
    WorkflowStage.DELIVERY_CENTRE: [
        WorkflowStage.READY_FOR_DELIVERY,
        WorkflowStage.OUT_FOR_DELIVERY,
        WorkflowStage.DELIVERED,
        WorkflowStage.ON_HOLD
    ],
    WorkflowStage.READY_FOR_DELIVERY: [
        WorkflowStage.OUT_FOR_DELIVERY,
        WorkflowStage.DELIVERED,
        WorkflowStage.ON_HOLD
    ],
    WorkflowStage.OUT_FOR_DELIVERY: [
        WorkflowStage.DELIVERED,
        WorkflowStage.DELIVERY_CENTRE,
        WorkflowStage.ON_HOLD
    ],
    WorkflowStage.ON_HOLD: [
        WorkflowStage.ALTERATION,
        WorkflowStage.DEEP_CLEANING,
        WorkflowStage.FINISHING,
        WorkflowStage.DELIVERY_CENTRE,
        WorkflowStage.READY_FOR_DELIVERY,
        WorkflowStage.CANCELLED
    ],
    WorkflowStage.DELIVERED: [],
    WorkflowStage.CANCELLED: []
}

def transition_garment_stage(
    db: Session,
    garment: Garment,
    new_stage: str,
    user_id: int,
    remarks: Optional[str] = None,
    photo_url: Optional[str] = None,
    department: Optional[str] = None,
    assigned_karigar_name: Optional[str] = None
) -> Tuple[Garment, OrderStatusHistory]:
    """
    Validate and execute a workflow stage transition for an individual garment.
    Updates the garment's status, creates a permanent audit log, and checks overall booking status.
    """
    old_stage = garment.current_stage

    # Check validity unless force transition
    valid_next = VALID_STAGE_TRANSITIONS.get(old_stage, [])
    if new_stage not in valid_next and old_stage != new_stage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stage transition from '{old_stage}' to '{new_stage}'. Allowed: {', '.join(valid_next)}"
        )

    # Update garment
    garment.current_stage = new_stage
    if assigned_karigar_name:
        garment.karigar_name = assigned_karigar_name
    garment.updated_at = datetime.utcnow()

    # Record history
    history = OrderStatusHistory(
        booking_id=garment.booking_id,
        garment_id=garment.id,
        previous_status=old_stage,
        new_status=new_stage,
        department=department or garment.category,
        changed_by_user_id=user_id,
        remarks=remarks,
        photo_url=photo_url
    )
    db.add(history)

    # Re-evaluate parent Booking status
    booking = db.query(Booking).filter(Booking.id == garment.booking_id).first()
    if booking:
        sibling_stages = [g.current_stage for g in booking.garments if g.id != garment.id]
        sibling_stages.append(new_stage)

        if all(s == WorkflowStage.DELIVERED.value for s in sibling_stages):
            booking.current_status = WorkflowStage.DELIVERED.value
        elif all(s in [WorkflowStage.READY_FOR_DELIVERY.value, WorkflowStage.DELIVERED.value] for s in sibling_stages):
            booking.current_status = WorkflowStage.READY_FOR_DELIVERY.value
        else:
            booking.current_status = new_stage

    db.commit()
    db.refresh(garment)
    return garment, history
