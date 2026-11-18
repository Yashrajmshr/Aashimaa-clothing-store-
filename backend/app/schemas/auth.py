from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None
    exp: Optional[int] = None
    type: Optional[str] = None

class LoginRequest(BaseModel):
    username_or_phone: str = Field(..., description="Username or mobile number")
    password: str = Field(..., min_length=4)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class SendOTPRequest(BaseModel):
    phone: str = Field(..., description="Registered 10-digit mobile number")
    booking_number: Optional[str] = Field(None, description="Optional booking # for track order")
    qr_token: Optional[str] = Field(None, description="Optional QR token for scan track")

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str = Field(..., min_length=4, max_length=6)
    booking_number: Optional[str] = None
    qr_token: Optional[str] = None

class PasswordResetRequest(BaseModel):
    phone_or_email: str
    new_password: str = Field(..., min_length=6)
    otp: str

class RoleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    phone: str
    full_name: str
    is_active: bool
    department: Optional[str] = None
    roles: List[RoleSchema] = []

    class Config:
        from_attributes = True

class CustomerAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer_id: int
    customer_name: str
    phone: str
    patron_tier: str
    booking_number: Optional[str] = None
