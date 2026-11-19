import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.notification import NotificationTemplate, NotificationLog
from backend.app.models.customer import Customer
from backend.app.models.booking import Booking

class NotificationService:
    @staticmethod
    def send_real_sms_fast2sms(phone: str, otp: str) -> Dict[str, Any]:
        """Dispatch real transactional SMS to Indian mobile numbers via Fast2SMS gateway."""
        api_key = settings.FAST2SMS_API_KEY or settings.SMS_API_KEY
        if not api_key:
            return {"success": False, "error": "FAST2SMS_API_KEY not set in .env"}

        clean_number = "".join(filter(str.isdigit, phone))[-10:]
        url = "https://www.fast2sms.com/dev/bulkV2"
        headers = {
            "authorization": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "variables_values": otp,
            "route": "otp",
            "numbers": clean_number
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=8)
            res_data = res.json()
            if res.status_code == 200 and res_data.get("return") is True:
                return {"success": True, "provider": "Fast2SMS", "response": res_data}
            return {"success": False, "provider": "Fast2SMS", "error": "Provider rejected the message"}
        except Exception:
            return {"success": False, "provider": "Fast2SMS", "error": "Provider request failed"}

    @staticmethod
    def send_real_sms_twilio(phone: str, message: str) -> Dict[str, Any]:
        """Dispatch real SMS via Twilio API."""
        if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER):
            return {"success": False, "error": "Twilio credentials not configured in .env"}

        clean_number = "".join(filter(str.isdigit, phone))
        formatted_phone = f"+91{clean_number[-10:]}" if len(clean_number) == 10 else f"+{clean_number}"

        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        data = {
            "From": settings.TWILIO_FROM_NUMBER,
            "To": formatted_phone,
            "Body": message
        }

        try:
            res = requests.post(url, auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN), data=data, timeout=8)
            if res.status_code in [200, 201]:
                return {"success": True, "provider": "Twilio", "sid": res.json().get("sid")}
            return {"success": False, "provider": "Twilio", "error": "Provider rejected the message"}
        except Exception:
            return {"success": False, "provider": "Twilio", "error": "Provider request failed"}

    @classmethod
    def send_otp(
        cls,
        db: Session,
        phone: str,
        otp: str,
        customer_name: Optional[str] = None,
        booking_number: Optional[str] = None,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Primary OTP Dispatcher:
        1. Attempts live SMS dispatch via configured provider (Fast2SMS / Twilio).
        2. Records delivery outcome without logging the verification secret.
        """
        clean_phone = "".join(filter(str.isdigit, phone))[-10:]
        sms_text = f"AASHIMA: Your order tracking verification code is {otp}. Valid for 10 mins. 581 Turab Nagar, Ghaziabad."
        
        # 1. Attempt Live Network Carrier SMS Dispatch
        sms_result = {"success": False, "provider": "None"}
        provider = settings.NOTIFICATION_PROVIDER.strip().lower()
        if provider == "fast2sms":
            sms_result = cls.send_real_sms_fast2sms(clean_phone, otp)
        elif provider == "twilio":
            sms_result = cls.send_real_sms_twilio(clean_phone, sms_text)

        # Record in database without including the OTP in message content.
        try:
            log = NotificationLog(
                recipient_phone=clean_phone,
                recipient_name=customer_name or "Atelier Patron",
                customer_id=customer_id,
                event_type="CUSTOMER_OTP_VERIFICATION",
                channel="SMS/WhatsApp",
                provider=sms_result.get("provider", "Direct Gateway"),
                message_content="Customer OTP verification message",
                status="Delivered" if sms_result.get("success") else "Dispatched",
                error_message=sms_result.get("error"),
                delivered_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            # Notification logging must not leak provider response bodies or secrets.
            pass

        return {
            "success": True,
            "sms_delivered": sms_result.get("success", False),
            "phone_masked": f"******{clean_phone[-4:]}",
            "message": f"Verification code dispatched to +91 ******{clean_phone[-4:]}"
        }

    @staticmethod
    def dispatch(
        db: Session,
        event_type: str,
        recipient_phone: str,
        context: Dict[str, Any],
        customer_id: Optional[int] = None,
        booking_id: Optional[int] = None,
        recipient_name: Optional[str] = None
    ) -> NotificationLog:
        """General workflow notifications (Intake confirmation, Trial ready, Pickup ready)."""
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.event_type == event_type,
            NotificationTemplate.is_active == True
        ).first()

        if template:
            channel = template.channel
            body = template.template_body
            for key, val in context.items():
                body = body.replace(f"{{{key}}}", str(val))
        else:
            channel = "SMS"
            body = f"AASHIMA Update: {event_type} for order #{context.get('booking_number', '')}."

        clean_phone = "".join(filter(str.isdigit, recipient_phone))[-10:]
        
        # Live SMS dispatch
        provider = settings.NOTIFICATION_PROVIDER.strip().lower()
        if provider == "fast2sms":
            NotificationService.send_real_sms_fast2sms(clean_phone, body)
        elif provider == "twilio":
            NotificationService.send_real_sms_twilio(clean_phone, body)

        log = NotificationLog(
            recipient_phone=clean_phone,
            recipient_name=recipient_name or context.get("customer_name"),
            customer_id=customer_id,
            booking_id=booking_id,
            event_type=event_type,
            channel=channel,
            provider=settings.NOTIFICATION_PROVIDER,
            message_content=body,
            status="Sent",
            delivered_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
