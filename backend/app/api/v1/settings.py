from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.auth import User
from backend.app.models.setting import BusinessSetting

router = APIRouter(prefix="/settings", tags=["Business Configuration & Hardware Setup"])

class SettingUpdatePayload(BaseModel):
    setting_key: str
    setting_value: str

@router.get("")
def list_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(BusinessSetting).all()
    return settings

@router.post("")
def update_setting(
    payload: SettingUpdatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setting = db.query(BusinessSetting).filter(BusinessSetting.setting_key == payload.setting_key).first()
    if not setting:
        setting = BusinessSetting(
            setting_key=payload.setting_key,
            setting_value=payload.setting_value,
            category="Custom"
        )
        db.add(setting)
    else:
        setting.setting_value = payload.setting_value

    db.commit()
    db.refresh(setting)
    return setting
