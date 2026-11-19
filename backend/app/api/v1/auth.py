import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from backend.app.core.config import settings
from backend.app.core.business_config import UserRole
from backend.app.models.auth import User
from backend.app.models.customer import Customer
from backend.app.models.booking import Booking
from backend.app.models.qr import GarmentQRToken
from backend.app.services.notification_service import NotificationService
from backend.app.schemas.auth import (
    Token,
    LoginRequest,
    RefreshTokenRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    PasswordResetRequest,
    UserResponse,
    CustomerAuthResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate Owner, Manager, Staff, Accountant, or Delivery Staff.
    Supports login via username or registered mobile number.
    """
    user = db.query(User).filter(
        ((User.username == request.username_or_phone) | (User.phone == request.username_or_phone)),
        User.is_deleted == False
    ).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/phone or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    primary_role = user.roles[0].name if user.roles else "Staff"

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "role": primary_role,
        "full_name": user.full_name
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        role=primary_role,
        full_name=user.full_name,
        user_id=user.id
    )

@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    primary_role = user.roles[0].name if user.roles else "Staff"
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "role": primary_role,
        "full_name": user.full_name
    }
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        role=primary_role,
        full_name=user.full_name,
        user_id=user.id
    )

@router.post("/customer/send-otp")
def send_customer_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """
    Generate and dispatch a 6-digit OTP for Customer verification.
    Verifies phone corresponds to a registered customer or matching booking/QR.
    Never exposes customer name or order details before OTP verification.
    """
    phone = "".join(filter(str.isdigit, request.phone))[-10:]

    # Validate phone format
    if len(phone) < 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 10-digit mobile number")

    # Strictly lookup patron record for THIS mobile number
    customer = db.query(Customer).filter(Customer.phone.endswith(phone), Customer.is_deleted == False).first()

    if not customer:
        # Keep the response generic so this endpoint does not enumerate customer accounts.
        return {"status": "success", "message": "If this number is registered, a verification code will be sent.", "expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60}

    if customer.otp_generated_at and (datetime.utcnow() - customer.otp_generated_at).total_seconds() < 60:
        return {
            "status": "success",
            "message": "If this number is registered, a verification code will be sent.",
            "expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60
        }

    # If booking_number supplied, resolve flexibly
    if request.booking_number:
        clean_num = request.booking_number.replace("#", "").strip().upper()
        candidates = [clean_num, f"ASH-{clean_num}", f"ASH{clean_num}"]
        booking = db.query(Booking).filter(
            Booking.booking_number.in_(candidates),
            Booking.is_deleted == False
        ).first()

        if not booking:
            booking = db.query(Booking).filter(
                Booking.booking_number.ilike(f"%{clean_num}%"),
                Booking.is_deleted == False
            ).first()

    if request.qr_token:
        qr = db.query(GarmentQRToken).filter(
            (GarmentQRToken.secure_token == request.qr_token) | 
            (GarmentQRToken.qr_code_identifier == request.qr_token)
        ).first()
        if not qr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR tag token not recognized")

    # Generate genuine cryptographically secure 6-digit OTP
    otp = str(secrets.randbelow(900000) + 100000)

    customer.last_otp = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), otp.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:10]
    customer.otp_generated_at = datetime.utcnow()
    customer.otp_attempts = 0
    db.commit()

    # Dispatch through the configured provider. OTP values and bearer links must not
    # be returned to the requesting browser or written to application logs.
    dispatch_res = NotificationService.send_otp(
        db=db,
        phone=phone,
        otp=otp,
        customer_name=customer.full_name if customer else "Atelier Patron",
        booking_number=request.booking_number,
        customer_id=customer.id if customer else None
    )

    return {
        "status": "success",
        "message": "If this number is registered, a verification code will be sent.",
        "expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60
    }

@router.post("/customer/verify-otp", response_model=CustomerAuthResponse)
def verify_customer_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Verify the 6-digit OTP and issue a customer-scoped JWT token.
    Grants access only to the customer's own garments, invoices, and timeline.
    """
    phone = "".join(filter(str.isdigit, request.phone))[-10:]
    customer = db.query(Customer).filter(Customer.phone.endswith(phone), Customer.is_deleted == False).first()
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code")

    if customer.otp_attempts >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code")

    # Verify OTP
    is_valid_otp = False
    submitted_otp = request.otp.strip()
    submitted_digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), submitted_otp.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:10]
    if customer.last_otp and hmac.compare_digest(customer.last_otp, submitted_digest):
        # Check expiry
        if customer.otp_generated_at and (datetime.utcnow() - customer.otp_generated_at).total_seconds() <= settings.OTP_EXPIRE_MINUTES * 60:
            is_valid_otp = True

    # Fallback in dev/sandbox
    if settings.ENVIRONMENT in {"development", "test"} and settings.DEFAULT_OTP_BYPASS and submitted_otp == settings.DEFAULT_OTP_BYPASS:
        is_valid_otp = True

    if not is_valid_otp:
        customer.otp_attempts += 1
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code")

    # Clear OTP after successful verification
    customer.last_otp = None
    customer.otp_attempts = 0
    db.commit()

    # Issue customer-scoped JWT token
    token_data = {
        "sub": f"customer_{customer.id}",
        "customer_id": customer.id,
        "role": UserRole.CUSTOMER,
        "phone": customer.phone,
        "customer_name": customer.full_name
    }
    access_token = create_access_token(token_data, expires_delta=timedelta(hours=48))

    return CustomerAuthResponse(
        access_token=access_token,
        customer_id=customer.id,
        customer_name=customer.full_name,
        phone=customer.phone,
        patron_tier=customer.patron_tier,
        booking_number=request.booking_number
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
