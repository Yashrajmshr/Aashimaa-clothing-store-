from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.auth import User
from backend.app.core.business_config import UserRole
from backend.app.services.report_service import (
    get_daybook_summary,
    get_karkhana_pipeline_summary,
    get_urgent_deliveries
)

router = APIRouter(prefix="/reports", tags=["Reporting & Operational Intelligence"])

@router.get("/dashboard-metrics", dependencies=[Depends(require_roles([UserRole.STAFF, UserRole.MANAGER, UserRole.ACCOUNTANT]))])
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    role_names = {role.name for role in current_user.roles}
    can_view_financials = UserRole.OWNER in role_names or UserRole.MANAGER in role_names or UserRole.ACCOUNTANT in role_names
    daybook = get_daybook_summary(db) if can_view_financials else {}
    pipeline = get_karkhana_pipeline_summary(db)
    urgent = get_urgent_deliveries(db)

    urgent_serialized = []
    for u in urgent:
        urgent_serialized.append({
            "booking_id": u.id,
            "booking_number": u.booking_number,
            "customer_name": u.customer.full_name,
            "urgent_reason": u.urgent_reason or "Expedited Delivery",
            "due_date": u.delivery_due_date.strftime("%d %b, %I:%M %p"),
            "stage": u.current_status
        })

    return {
        "daybook": daybook,
        "pipeline": pipeline,
        "urgent_orders": urgent_serialized,
        "urgent_count": len(urgent_serialized)
    }
