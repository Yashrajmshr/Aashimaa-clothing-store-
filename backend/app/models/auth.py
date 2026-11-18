from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, SoftDeleteMixin

role_permission_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

user_role_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "booking:create", "billing:view"
    name = Column(String(150), nullable=False)
    module = Column(String(50), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    roles = relationship("Role", secondary=role_permission_table, back_populates="permissions")

class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # Owner, Manager, Staff, Accountant, Delivery Staff, Customer
    description = Column(String(255), nullable=True)
    is_system_role = Column(Boolean, default=True, nullable=False)

    users = relationship("User", secondary=user_role_table, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission_table, back_populates="roles")

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    department = Column(String(50), nullable=True) # Alteration, Deep Cleaning, Finishing, Counter, Delivery
    last_login = Column(DateTime, nullable=True)

    roles = relationship("Role", secondary=user_role_table, back_populates="users", lazy="joined")
    activities = relationship("StaffActivity", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

class StaffActivity(Base, TimestampMixin):
    __tablename__ = "staff_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # STAGE_UPDATE, PAYMENT_COLLECTED, QR_PRINT, ORDER_CREATE
    entity_type = Column(String(50), nullable=False) # Garment, Booking, Payment, Customer
    entity_id = Column(String(50), nullable=False)
    details = Column(Text, nullable=True) # JSON or formatted description
    ip_address = Column(String(45), nullable=True)

    user = relationship("User", back_populates="activities")

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    table_name = Column(String(50), nullable=False, index=True)
    record_id = Column(String(50), nullable=False)
    old_values = Column(Text, nullable=True) # JSON dump of old state
    new_values = Column(Text, nullable=True) # JSON dump of new state
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)

    user = relationship("User", back_populates="audit_logs")
