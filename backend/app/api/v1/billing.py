import os
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.auth import User
from backend.app.models.billing import Invoice, Payment, Expense, GSTConfiguration
from backend.app.schemas.billing import (
    InvoiceCreate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    ExpenseCreate,
    ExpenseResponse,
    DaybookSummaryResponse
)
from backend.app.services.billing_service import create_invoice_for_booking, record_payment
from backend.app.services.report_service import get_daybook_summary
from backend.app.core.business_config import UserRole

router = APIRouter(prefix="/billing", tags=["Financials, Invoicing & Daybook Ledger"])

@router.get("/daybook-summary", response_model=DaybookSummaryResponse)
def get_daybook(
    date_str: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    target = None
    if date_str:
        try:
            target = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")
    return get_daybook_summary(db, target)

@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(
    booking_id: Optional[int] = Query(None),
    invoice_type: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Invoice).filter(Invoice.is_deleted == False)
    if booking_id:
        query = query.filter(Invoice.booking_id == booking_id)
    if invoice_type:
        query = query.filter(Invoice.invoice_type == invoice_type)
    return query.order_by(Invoice.invoice_date.desc()).offset(skip).limit(limit).all()

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invoice = create_invoice_for_booking(
        db=db,
        booking_id=payload.booking_id,
        invoice_type=payload.invoice_type,
        discount_amount=payload.discount_amount,
        extra_charges=payload.extra_charges,
        user_id=current_user.id
    )
    return invoice

@router.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if not invoice.pdf_path:
        raise HTTPException(status_code=404, detail="PDF invoice file not generated")

    abs_path = os.path.join(os.getcwd(), invoice.pdf_path.lstrip("/"))
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Invoice PDF file missing from disk")

    return FileResponse(abs_path, media_type="application/pdf", filename=f"{invoice.invoice_number}.pdf")

@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_200_OK)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.is_deleted == False).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.soft_delete()
    db.commit()
    return {
        "status": "success",
        "message": f"Invoice {invoice.invoice_number} deleted successfully",
        "invoice_id": invoice_id
    }

@router.get("/payments", response_model=List[PaymentResponse])
def list_payments(
    booking_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Payment).filter(Payment.is_deleted == False)
    if booking_id:
        query = query.filter(Payment.booking_id == booking_id)
    return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def add_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment, receipt = record_payment(
        db=db,
        booking_id=payload.booking_id,
        amount=payload.amount,
        payment_type=payload.payment_type,
        payment_mode=payload.payment_mode,
        transaction_id=payload.transaction_id,
        notes=payload.notes,
        user_id=current_user.id
    )
    return payment

@router.get("/expenses", response_model=List[ExpenseResponse])
def list_expenses(
    category: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Expense).filter(Expense.is_deleted == False)
    if category:
        query = query.filter(Expense.category == category)
    return query.order_by(Expense.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = db.query(Expense).count() + 1
    exp_num = f"EXP-{datetime.utcnow().year}-{count:04d}"

    expense = Expense(
        expense_number=exp_num,
        category=payload.category,
        division=payload.division,
        title=payload.title,
        amount=payload.amount,
        payment_mode=payload.payment_mode,
        paid_to=payload.paid_to,
        notes=payload.notes,
        approved_by_user_id=current_user.id
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.is_deleted == False).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense entry not found")

    expense.soft_delete()
    db.commit()
    return {
        "status": "success",
        "message": f"Expense {expense.expense_number} deleted successfully",
        "expense_id": expense_id
    }
