from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.customer import Customer, CustomerAddress
from backend.app.models.auth import User
from backend.app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from backend.app.core.business_config import UserRole

router = APIRouter(prefix="/customers", tags=["Customer Registry"])

@router.get("", response_model=List[CustomerResponse])
def list_customers(
    search: Optional[str] = Query(None, description="Search by name, phone, or customer code"),
    patron_tier: Optional[str] = Query(None),
    has_dues: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Customer).filter(Customer.is_deleted == False)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Customer.full_name.ilike(search_fmt),
                Customer.phone.ilike(search_fmt),
                Customer.customer_code.ilike(search_fmt),
                Customer.unit_reference.ilike(search_fmt)
            )
        )

    if patron_tier:
        query = query.filter(Customer.patron_tier == patron_tier)

    if has_dues is True:
        query = query.filter(Customer.outstanding_dues > 0)

    customers = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check phone uniqueness
    existing = db.query(Customer).filter(Customer.phone == payload.phone.strip(), Customer.is_deleted == False).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this phone number already exists")

    count = db.query(Customer).count() + 1
    code = f"CUST-{count:04d}"

    customer = Customer(
        customer_code=code,
        full_name=payload.full_name,
        phone=payload.phone.strip(),
        email=payload.email,
        patron_tier=payload.patron_tier,
        unit_reference=payload.unit_reference,
        notes=payload.notes
    )
    db.add(customer)
    db.flush()

    if payload.address:
        addr = CustomerAddress(
            customer_id=customer.id,
            address_type=payload.address.address_type,
            address_line1=payload.address.address_line1,
            address_line2=payload.address.address_line2,
            landmark=payload.address.landmark,
            city=payload.address.city,
            state=payload.address.state,
            pincode=payload.address.pincode,
            is_default=True
        )
        db.add(addr)

    db.commit()
    db.refresh(customer)
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if payload.full_name is not None:
        customer.full_name = payload.full_name
    if payload.email is not None:
        customer.email = payload.email
    if payload.patron_tier is not None:
        customer.patron_tier = payload.patron_tier
    if payload.unit_reference is not None:
        customer.unit_reference = payload.unit_reference
    if payload.notes is not None:
        customer.notes = payload.notes

    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}", status_code=status.HTTP_200_OK)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft-delete a customer patron record from the registry.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.soft_delete()
    db.commit()
    return {
        "status": "success",
        "message": f"Customer '{customer.full_name}' ({customer.customer_code}) deleted successfully",
        "customer_id": customer_id
    }
