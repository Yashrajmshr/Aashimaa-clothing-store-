import io
import base64
import uuid
import hmac
import hashlib
from typing import Dict, Any, List
import qrcode
from qrcode.image.pil import PilImage
from backend.app.core.config import settings

def generate_secure_token(garment_code: str) -> str:
    """Generate unpredictable HMAC-signed tracking token."""
    raw_token = f"{garment_code}_{uuid.uuid4().hex}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        raw_token.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()[:16]
    return f"token_sec_{raw_token}_{signature}"

def generate_qr_data_uri(payload_url: str) -> str:
    """Generate high-contrast Base64 PNG Data URI for thermal printing and screens."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def generate_thermal_slip_text(
    shop_name: str,
    address: str,
    phone: str,
    booking_number: str,
    customer_name: str,
    customer_phone: str,
    unit_reference: str,
    garment_code: str,
    article_tag: str,
    garment_name: str,
    services: List[str],
    due_date_str: str,
    karigar_name: str,
    rack_location: str,
    advance_paid: str,
    balance_due: str,
    width_mode: str = "80mm"
) -> str:
    """
    Format monospace ESC/POS thermal text slip matching Google Stitch thermal drawer.
    32 chars per line for 58mm, 48 chars per line for 80mm.
    """
    line_width = 48 if width_mode == "80mm" else 32
    sep = "=" * line_width
    dash = "-" * line_width

    lines = []
    lines.append(shop_name.center(line_width))
    lines.append("ATELIER & BESPOKE TAILORING".center(line_width))
    lines.append(address[:line_width].center(line_width))
    lines.append(f"Phone: {phone}".center(line_width))
    lines.append(sep)
    lines.append(f"TAG: {garment_code}".ljust(line_width - 16) + f"RACK: {rack_location}".rjust(16))
    lines.append(f"BOOKING: #{booking_number}".ljust(line_width))
    lines.append(dash)
    lines.append(f"CLIENT : {customer_name[:line_width-9]}")
    lines.append(f"PHONE  : {customer_phone}  {unit_reference or ''}")
    lines.append(dash)
    lines.append(f"ARTICLE: {garment_name} [{article_tag or 'N/A'}]")
    lines.append("SERVICES:")
    for s in services:
        lines.append(f" * {s}")
    lines.append(dash)
    lines.append(f"KARIGAR: {karigar_name or 'Unassigned'}")
    lines.append(f"DUE DT : {due_date_str}")
    lines.append(dash)
    lines.append(f"ADVANCE: Rs {advance_paid}".ljust(line_width // 2) + f"DUE: Rs {balance_due}".rjust(line_width // 2))
    lines.append(sep)
    lines.append("CLAIM SLIP - TEAR HERE".center(line_width))
    lines.append("Present this tag for trial & handover".center(line_width))
    lines.append("www.aashima-atelier.in/track".center(line_width))
    lines.append("\n\n\n")

    return "\n".join(lines)
