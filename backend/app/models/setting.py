from sqlalchemy import Column, Integer, String, Text, Boolean
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class BusinessSetting(Base, TimestampMixin):
    __tablename__ = "business_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    data_type = Column(String(20), default="string", nullable=False) # string, integer, boolean, json, decimal
    category = Column(String(50), default="General", nullable=False, index=True) # General, Billing, Printing, Notification, Workshop
    description = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
