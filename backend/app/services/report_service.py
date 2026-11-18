from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.billing import Payment, Invoice, Expense
from backend.app.models.booking import Booking, Garment
from backend.app.models.customer import Customer
from backend.app.core.business_config import WorkflowStage

def get_daybook_summary(db: Session, target_date: Optional[date] = None) -> Dict[str, Any]:
    if not target_date:
        target_date = datetime.utcnow().date()

    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date, datetime.max.time())

    # Payments collected today
    payments_today = db.query(Payment).filter(
        Payment.created_at >= start_dt,
        Payment.created_at <= end_dt
    ).all()

    collected_total = sum(p.amount for p in payments_today) or Decimal("0.00")
    cash_total = sum(p.amount for p in payments_today if p.payment_mode == "Cash") or Decimal("0.00")
    upi_total = sum(p.amount for p in payments_today if p.payment_mode == "UPI") or Decimal("0.00")
    card_total = sum(p.amount for p in payments_today if p.payment_mode == "Card") or Decimal("0.00")

    # Pending balance across all active bookings
    active_bookings = db.query(Booking).filter(
        Booking.payment_status.in_(["Unpaid", "Partial"])
    ).all()
    pending_balance_total = sum(b.balance_due for b in active_bookings) or Decimal("0.00")

    # Invoices billed today
    invoices_today = db.query(Invoice).filter(
        Invoice.created_at >= start_dt,
        Invoice.created_at <= end_dt
    ).all()
    slips_count = len(invoices_today)
    avg_ticket = (sum(i.grand_total for i in invoices_today) / slips_count) if slips_count > 0 else Decimal("0.00")

    return {
        "collected_today": collected_total,
        "pending_balance": pending_balance_total,
        "cash_collected": cash_total,
        "upi_collected": upi_total,
        "card_collected": card_total,
        "active_shift": "Counter Shift #1 Active",
        "slips_billed_count": slips_count,
        "avg_ticket_value": avg_ticket,
        "date_str": target_date.strftime("%d %b %Y")
    }

def get_karkhana_pipeline_summary(db: Session) -> Dict[str, Any]:
    garments = db.query(Garment).filter(
        Garment.current_stage != WorkflowStage.DELIVERED.value,
        Garment.current_stage != WorkflowStage.CANCELLED.value
    ).all()

    total_in_floor = len(garments)
    alt_count = sum(1 for g in garments if g.current_stage == WorkflowStage.ALTERATION.value)
    wash_count = sum(1 for g in garments if g.current_stage == WorkflowStage.DEEP_CLEANING.value)
    steam_count = sum(1 for g in garments if g.current_stage == WorkflowStage.FINISHING.value)
    ready_count = sum(1 for g in garments if g.current_stage == WorkflowStage.READY_FOR_DELIVERY.value)
    transit_count = sum(1 for g in garments if g.current_stage in [WorkflowStage.DELIVERY_CENTRE.value, WorkflowStage.OUT_FOR_DELIVERY.value])

    return {
        "total_in_floor": total_in_floor,
        "alteration_count": alt_count,
        "deep_clean_count": wash_count,
        "steam_finishing_count": steam_count,
        "trial_ready_count": ready_count,
        "transit_logistics_count": transit_count
    }

def get_urgent_deliveries(db: Session) -> List[Booking]:
    now = datetime.utcnow()
    two_days_later = now + timedelta(days=2)

    urgent_list = db.query(Booking).filter(
        (Booking.is_urgent == True) | (Booking.delivery_due_date <= two_days_later),
        Booking.current_status != WorkflowStage.DELIVERED.value
    ).all()
    return urgent_list
