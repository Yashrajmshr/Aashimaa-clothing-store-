import os
import json
import urllib.parse
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
            return {"success": False, "provider": "Fast2SMS", "error": res_data.get("message", "Fast2SMS error")}
        except Exception as e:
            return {"success": False, "provider": "Fast2SMS", "error": str(e)}

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
            return {"success": False, "provider": "Twilio", "error": res.text}
        except Exception as e:
            return {"success": False, "provider": "Twilio", "error": str(e)}

    @staticmethod
    def generate_whatsapp_link(phone: str, otp: str, booking_number: Optional[str] = None) -> str:
        """Generate direct WhatsApp click-to-receive link for seamless zero-friction verification."""
        clean_number = "".join(filter(str.isdigit, phone))[-10:]
        intake_ref = f" for booking #{booking_number}" if booking_number else ""
        msg = (
            f"Namaste from AASHIMA Atelier (581, Turab Nagar, Ghaziabad).\n\n"
            f"Your login & order tracking verification code{intake_ref} is:\n"
            f"🔑 *{otp}*\n\n"
            f"Valid for 10 minutes. For assistance call +91 98102 44321."
        )
        encoded_msg = urllib.parse.quote(msg)
        return f"https://api.whatsapp.com/send?phone=91{clean_number}&text={encoded_msg}"

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
        2. Generates WhatsApp direct chat verification URL.
        3. Prints high-visibility real-time alert in server terminal.
        4. Logs into notification_logs table.
        """
        clean_phone = "".join(filter(str.isdigit, phone))[-10:]
        sms_text = f"AASHIMA: Your order tracking verification code is {otp}. Valid for 10 mins. 581 Turab Nagar, Ghaziabad."
        
        # 1. Attempt Live Network Carrier SMS Dispatch
        sms_result = {"success": False, "provider": "None"}
        if settings.FAST2SMS_API_KEY or (settings.SMS_API_KEY and settings.NOTIFICATION_PROVIDER == "fast2sms"):
            sms_result = cls.send_real_sms_fast2sms(clean_phone, otp)
        elif settings.TWILIO_ACCOUNT_SID:
            sms_result = cls.send_real_sms_twilio(clean_phone, sms_text)

        # 2. WhatsApp Direct Verification Link
        wa_link = cls.generate_whatsapp_link(clean_phone, otp, booking_number)

        # 3. Terminal Realtime Broadcast
        delivery_mode = "Live SMS (Fast2SMS/Twilio)" if sms_result.get("success") else "Console & WhatsApp Gateway"
        print("\n" + "=" * 65)
        print(" [OTP DISPATCH] AASHIMA ATELIER SECURE VERIFICATION CODE")
        print(f" Recipient Phone : +91 {clean_phone}")
        print(f" 6-Digit OTP     : >>> {otp} <<<")
        print(f" Booking Ref     : #{booking_number or 'Atelier-Tracking'}")
        print(f" Delivery Mode   : {delivery_mode}")
        if sms_result.get("error"):
            print(f" SMS Provider Note: {sms_result['error']}")
        print(f" Direct WhatsApp : {wa_link}")
        print("=" * 65 + "\n")

        # 4. Record in database NotificationLog
        try:
            log = NotificationLog(
                recipient_phone=clean_phone,
                recipient_name=customer_name or "Atelier Patron",
                customer_id=customer_id,
                event_type="CUSTOMER_OTP_VERIFICATION",
                channel="SMS/WhatsApp",
                provider=sms_result.get("provider", "Direct Gateway"),
                message_content=sms_text,
                status="Delivered" if sms_result.get("success") else "Dispatched",
                error_message=sms_result.get("error"),
                delivered_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[NotificationLog Error]: {e}")

        return {
            "success": True,
            "sms_delivered": sms_result.get("success", False),
            "phone_masked": f"******{clean_phone[-4:]}",
            "whatsapp_url": wa_link,
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
        if settings.FAST2SMS_API_KEY or settings.SMS_API_KEY:
            NotificationService.send_real_sms_fast2sms(clean_phone, body)
        elif settings.TWILIO_ACCOUNT_SID:
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
