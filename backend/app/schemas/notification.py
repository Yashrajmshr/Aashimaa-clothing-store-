from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class NotificationLogResponse(BaseModel):
    id: int
    recipient_phone: str
    recipient_name: Optional[str] = None
    event_type: str
    channel: str
    provider: str
    message_content: str
    status: str
    retry_count: int
    created_at: datetime
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationTemplateResponse(BaseModel):
    id: int
    event_type: str
    channel: str
    title: str
    template_body: str
    is_active: bool

    class Config:
        from_attributes = True
