import os
import json
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.core.security import get_password_hash
from backend.app.core.business_config import (
    DEFAULT_SERVICES,
    BusinessDivision,
    ServiceCategory,
    WorkflowStage,
    UserRole
)
from backend.app.models import (
    Role,
    Permission,
    User,
    Customer,
    CustomerAddress,
    Service,
    ServicePricing,
    TailoringMeasurementTemplate,
    GSTConfiguration,
    NotificationTemplate,
    BusinessSetting,
    Booking,
    Garment,
    BookingService,
    GarmentMeasurement,
    GarmentPhotograph,
    GarmentQRToken,
    QRScanHistory,
    DepartmentAssignment,
    OrderStatusHistory,
    Payment,
    PaymentReceipt,
    Invoice,
    InvoiceItem,
    Delivery,
    TransportationUpdate,
    Expense,
    Feedback,
    SupportTicket,
    NotificationLog,
    StaffActivity,
    AuditLog
)

def purge_synthetic_data(db):
    """Purge all synthetic, demo, and transactional data for a clean production state."""
    print("[Seed] Purging all synthetic customer, order, log, and transactional data...")
    # Delete child tables first
    db.query(TransportationUpdate).delete()
    db.query(Delivery).delete()
    db.query(InvoiceItem).delete()
    db.query(Invoice).delete()
    db.query(PaymentReceipt).delete()
    db.query(Payment).delete()
    db.query(OrderStatusHistory).delete()
    db.query(DepartmentAssignment).delete()
    db.query(QRScanHistory).delete()
    db.query(GarmentQRToken).delete()
    db.query(GarmentPhotograph).delete()
    db.query(GarmentMeasurement).delete()
    db.query(BookingService).delete()
    db.query(Garment).delete()
    db.query(Booking).delete()
    db.query(CustomerAddress).delete()
    db.query(Customer).delete()
    db.query(Expense).delete()
    db.query(Feedback).delete()
    db.query(SupportTicket).delete()
    db.query(NotificationLog).delete()
    db.query(StaffActivity).delete()
    db.query(AuditLog).delete()
    # Remove synthetic sample staff users (keep only primary owner account)
    db.query(User).filter(User.username.in_(["manager", "master_tailor", "accountant", "delivery"])).delete(synchronize_session=False)
    db.commit()
    print("[Seed] All synthetic transactional and demo staff data successfully purged!")

def run_seed(clean_synthetic=True):
    print("[Seed] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if clean_synthetic:
            purge_synthetic_data(db)

        # 1. Seed Roles
        print("[Seed] Seeding Roles...")
        roles_data = [
            (UserRole.OWNER, "Full administrative and financial authority over atelier operations"),
            (UserRole.MANAGER, "Workshop and floor supervisor with order lifecycle privileges"),
            (UserRole.STAFF, "Tailors, karigars, and finishing counter operators"),
            (UserRole.ACCOUNTANT, "Billing, invoice generation, daybook reconciliation"),
            (UserRole.DELIVERY_STAFF, "Logistics, package dispatch, and proof-of-delivery collection"),
            (UserRole.CUSTOMER, "Public portal user with read-only tracking and invoice access")
        ]
        role_map = {}
        for role_name, desc in roles_data:
            role = db.query(Role).filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=desc, is_system_role=True)
                db.add(role)
                db.flush()
            role_map[role_name] = role

        # 2. Seed Permissions
        print("[Seed] Seeding Permissions...")
        permissions_list = [
            ("booking:create", "Create New Booking", "Bookings"),
            ("booking:read", "View Bookings", "Bookings"),
            ("booking:update", "Update Booking Details", "Bookings"),
            ("booking:delete", "Cancel/Delete Booking", "Bookings"),
            ("garment:stage_update", "Update Garment Workflow Stage", "Workshop"),
            ("garment:measurements", "Record Tailoring Measurements", "Workshop"),
            ("qr:generate", "Generate Garment QR Tokens", "QR System"),
            ("qr:scan", "Scan QR Code for Stage Tracking", "QR System"),
            ("qr:reprint", "Reprint Garment Tags", "QR System"),
            ("billing:invoice_create", "Create GST/Non-GST Invoice", "Billing"),
            ("billing:payment_collect", "Collect Advance/Balance Payments", "Billing"),
            ("billing:view_ledger", "View Daybook Ledger", "Billing"),
            ("customer:create", "Register New Customer", "Customers"),
            ("customer:read", "View Customer Dossier", "Customers"),
            ("reports:view", "View Analytics and Daybook", "Reports"),
            ("settings:manage", "Manage Business Settings", "Settings"),
            ("staff:manage", "Manage Staff and Karigars", "Staff"),
            ("delivery:manage", "Manage Dispatches and POD", "Delivery")
        ]
        perm_objs = []
        for code, name, module in permissions_list:
            perm = db.query(Permission).filter_by(code=code).first()
            if not perm:
                perm = Permission(code=code, name=name, module=module)
                db.add(perm)
                db.flush()
            perm_objs.append(perm)
        
        # Assign all permissions to Owner
        role_map[UserRole.OWNER].permissions = perm_objs

        # 3. Seed Primary Owner Account Only (zero synthetic staff accounts)
        print("[Seed] Seeding Primary Owner Account...")
        users_data = [
            {
                "username": "owner",
                "email": "owner@aashima.in",
                "full_name": "AASHIMA Owner",
                "phone": "9810244321",
                "password": "Password@123",
                "role": UserRole.OWNER
            }
        ]
        created_users = {}
        for u in users_data:
            user = db.query(User).filter((User.username == u["username"]) | (User.phone == u["phone"])).first()
            if not user:
                user = User(
                    username=u["username"],
                    email=u["email"],
                    full_name=u["full_name"],
                    phone=u["phone"],
                    hashed_password=get_password_hash(u["password"]),
                    is_active=True,
                    is_verified=True
                )
                user.roles.append(role_map[u["role"]])
                db.add(user)
                db.flush()
            created_users[u["username"]] = user

        # 4. Seed Services and Pricing Tiers (Foundational catalog)
        print("[Seed] Seeding Default Services & Pricing...")
        for s in DEFAULT_SERVICES:
            service = db.query(Service).filter_by(name=s["name"]).first()
            if not service:
                service = Service(
                    code=f"SRV-{secrets.token_hex(3).upper()}",
                    name=s["name"],
                    category=s["category"].value,
                    division=s["division"].value,
                    hsn_sac=s["hsn_sac"],
                    turnaround_days=s["turnaround_days"],
                    requires_measurement=s["requires_measurement"],
                    is_active=True
                )
                db.add(service)
                db.flush()

                # Add Standard Pricing Tier
                pricing = ServicePricing(
                    service_id=service.id,
                    tier_name="Standard",
                    base_price=Decimal(str(s["base_price"])),
                    gst_rate=Decimal(str(s["gst_rate"])),
                    is_current=True
                )
                db.add(pricing)

                # Add Urgent/Express Pricing Tier (+50%)
                urgent_pricing = ServicePricing(
                    service_id=service.id,
                    tier_name="Express",
                    base_price=Decimal(str(s["base_price"])) * Decimal("1.5"),
                    gst_rate=Decimal(str(s["gst_rate"])),
                    is_current=True
                )
                db.add(urgent_pricing)

        # 5. Seed Tailoring Measurement Templates (Men's Bespoke & Women's Couture)
        print("[Seed] Seeding Men's & Women's Measurement Templates...")
        measurement_templates = [
            # ---------------- MEN'S BESPOKE TAILORING ----------------
            {
                "garment_type": "MENS_COAT_BLAZER",
                "template_name": "Men's Bespoke Coat / Blazer",
                "gender": "Men",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Coat Length", "min": 25.0, "max": 36.0},
                    {"name": "chest", "label": "Chest", "min": 32.0, "max": 56.0},
                    {"name": "stomach", "label": "Stomach / Waist", "min": 28.0, "max": 54.0},
                    {"name": "hip", "label": "Seat / Hip", "min": 32.0, "max": 56.0},
                    {"name": "shoulder", "label": "Across Shoulder", "min": 15.0, "max": 23.0},
                    {"name": "cross_back", "label": "Cross Back", "min": 14.0, "max": 22.0},
                    {"name": "sleeve_length", "label": "Sleeve Length", "min": 20.0, "max": 29.0},
                    {"name": "bicep", "label": "Bicep Round", "min": 11.0, "max": 20.0},
                    {"name": "cuff", "label": "Cuff / Wrist", "min": 8.0, "max": 13.0},
                    {"name": "neck", "label": "Collar / Neck", "min": 13.5, "max": 20.0}
                ],
                "directives": "Specify canvas type, vent style (single/double), and lapel cut (notch/peak)."
            },
            {
                "garment_type": "MENS_SHIRT",
                "template_name": "Men's Formal / Casual Shirt",
                "gender": "Men",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Shirt Length", "min": 25.0, "max": 35.0},
                    {"name": "chest", "label": "Chest", "min": 32.0, "max": 56.0},
                    {"name": "waist", "label": "Waist / Taper", "min": 28.0, "max": 54.0},
                    {"name": "hip", "label": "Bottom / Seat", "min": 32.0, "max": 56.0},
                    {"name": "shoulder", "label": "Across Shoulder", "min": 15.0, "max": 23.0},
                    {"name": "sleeve_length", "label": "Sleeve Length", "min": 8.0, "max": 29.0},
                    {"name": "bicep", "label": "Arm / Bicep", "min": 11.0, "max": 20.0},
                    {"name": "cuff", "label": "Cuff Round", "min": 7.5, "max": 12.0},
                    {"name": "collar", "label": "Collar / Neck", "min": 13.5, "max": 20.0}
                ],
                "directives": "Specify collar style (spread/mandarin/button-down), pocket, and fit."
            },
            {
                "garment_type": "MENS_PANT_TROUSER",
                "template_name": "Men's Formal Trouser / Pant",
                "gender": "Men",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Outseam Length", "min": 34.0, "max": 48.0},
                    {"name": "inseam", "label": "Inseam Length", "min": 26.0, "max": 38.0},
                    {"name": "waist", "label": "Waist", "min": 26.0, "max": 52.0},
                    {"name": "hip", "label": "Seat / Hip", "min": 32.0, "max": 56.0},
                    {"name": "thigh", "label": "Thigh Round", "min": 18.0, "max": 34.0},
                    {"name": "knee", "label": "Knee Round", "min": 14.0, "max": 24.0},
                    {"name": "bottom", "label": "Bottom / Hem Opening", "min": 12.0, "max": 20.0},
                    {"name": "crotch_rise", "label": "Fork / Crotch Rise", "min": 22.0, "max": 34.0}
                ],
                "directives": "Specify flat front or pleats, cross/straight pocket, and belt loop style."
            },
            {
                "garment_type": "MENS_KURTA_PAJAMA",
                "template_name": "Men's Kurta & Pajama / Churidar",
                "gender": "Men",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "kurta_length", "label": "Kurta Length", "min": 34.0, "max": 48.0},
                    {"name": "chest", "label": "Chest", "min": 32.0, "max": 56.0},
                    {"name": "waist", "label": "Waist", "min": 28.0, "max": 54.0},
                    {"name": "hip", "label": "Hip", "min": 32.0, "max": 56.0},
                    {"name": "shoulder", "label": "Shoulder", "min": 15.0, "max": 23.0},
                    {"name": "sleeve_length", "label": "Sleeve Length", "min": 20.0, "max": 29.0},
                    {"name": "neck", "label": "Mandarin Collar / Neck", "min": 14.0, "max": 20.0},
                    {"name": "pajama_length", "label": "Pajama / Churidar Length", "min": 36.0, "max": 54.0},
                    {"name": "pajama_bottom", "label": "Ankle / Mori Opening", "min": 9.0, "max": 18.0}
                ],
                "directives": "Specify straight or Pathani cut, placket buttons, and waist drawstring/elastic."
            },
            {
                "garment_type": "MENS_SHERWANI_BANDHGALA",
                "template_name": "Men's Sherwani / Bandhgala / Jodhpuri",
                "gender": "Men",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Full Length", "min": 28.0, "max": 50.0},
                    {"name": "chest", "label": "Chest", "min": 32.0, "max": 56.0},
                    {"name": "waist", "label": "Waist", "min": 28.0, "max": 54.0},
                    {"name": "hip", "label": "Seat / Hip", "min": 32.0, "max": 56.0},
                    {"name": "shoulder", "label": "Across Shoulder", "min": 15.0, "max": 23.0},
                    {"name": "cross_back", "label": "Cross Back", "min": 14.0, "max": 22.0},
                    {"name": "sleeve_length", "label": "Sleeve Length", "min": 20.0, "max": 29.0},
                    {"name": "armhole", "label": "Armhole Round", "min": 15.0, "max": 24.0},
                    {"name": "collar_neck", "label": "Bandhgala Collar", "min": 14.0, "max": 20.0},
                    {"name": "cuff", "label": "Wrist Opening", "min": 8.0, "max": 12.0}
                ],
                "directives": "Specify chest canvas structure, button style, front slit, and pocket square welt."
            },
            {
                "garment_type": "MENS_WAISTCOAT_NEHRU",
                "template_name": "Men's Waistcoat / Nehru Jacket",
                "gender": "Men",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Jacket Length", "min": 23.0, "max": 33.0},
                    {"name": "chest", "label": "Chest", "min": 32.0, "max": 56.0},
                    {"name": "waist", "label": "Waist", "min": 28.0, "max": 54.0},
                    {"name": "hip", "label": "Bottom / Hip", "min": 32.0, "max": 56.0},
                    {"name": "shoulder", "label": "Shoulder", "min": 15.0, "max": 22.0},
                    {"name": "armhole", "label": "Armhole Depth", "min": 16.0, "max": 24.0},
                    {"name": "neck", "label": "Mandarin / V-Neck", "min": 14.0, "max": 20.0}
                ],
                "directives": "Specify mandarin or V-neck cut, welt pockets, and lining fabric."
            },
            # ---------------- WOMEN'S COUTURE TAILORING ----------------
            {
                "garment_type": "BLOUSE",
                "template_name": "Women's Designer Blouse",
                "gender": "Women",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Full Length", "min": 10.0, "max": 20.0},
                    {"name": "chest", "label": "Upper Bust / Chest", "min": 26.0, "max": 54.0},
                    {"name": "bust", "label": "Apex Bust", "min": 26.0, "max": 54.0},
                    {"name": "waist", "label": "Underbust / Waist", "min": 22.0, "max": 48.0},
                    {"name": "shoulder", "label": "Across Shoulder", "min": 10.0, "max": 20.0},
                    {"name": "armhole", "label": "Armhole Round", "min": 12.0, "max": 24.0},
                    {"name": "sleeve_length", "label": "Sleeve Length", "min": 3.0, "max": 26.0},
                    {"name": "sleeve_round", "label": "Sleeve Opening / Bicep", "min": 8.0, "max": 20.0},
                    {"name": "front_neck", "label": "Front Neck Depth", "min": 4.0, "max": 12.0},
                    {"name": "back_neck", "label": "Back Neck Depth", "min": 3.0, "max": 14.0}
                ],
                "directives": "Specify padding, side margin allowance, hook placement (front/back), and dori/latkan."
            },
            {
                "garment_type": "KURTI",
                "template_name": "Women's Kurti / Kameez",
                "gender": "Women",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Full Length", "min": 30.0, "max": 56.0},
                    {"name": "chest", "label": "Bust", "min": 28.0, "max": 56.0},
                    {"name": "waist", "label": "Waist", "min": 24.0, "max": 50.0},
                    {"name": "hip", "label": "Hip", "min": 30.0, "max": 60.0},
                    {"name": "shoulder", "label": "Shoulder", "min": 11.0, "max": 20.0},
                    {"name": "armhole", "label": "Armhole", "min": 12.0, "max": 24.0},
                    {"name": "sleeve_length", "label": "Sleeve Length", "min": 4.0, "max": 26.0},
                    {"name": "slit_opening", "label": "Side Slit Opening", "min": 14.0, "max": 26.0}
                ],
                "directives": "Specify lining requirement, neck shape, side slit depth, and hem finish."
            },
            {
                "garment_type": "LEHENGA",
                "template_name": "Women's Bridal Flared Lehenga",
                "gender": "Women",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Skirt Length", "min": 34.0, "max": 50.0},
                    {"name": "waist", "label": "Waist Band", "min": 24.0, "max": 48.0},
                    {"name": "hip", "label": "Hip Flare", "min": 30.0, "max": 56.0},
                    {"name": "flare_ghera", "label": "Ghera / Flare Circumference", "min": 100.0, "max": 300.0},
                    {"name": "can_can_layers", "label": "Can-Can Layers", "min": 0.0, "max": 5.0}
                ],
                "directives": "Specify buckram border stiffness, side zip & hook, and can-can layering."
            },
            {
                "garment_type": "WOMENS_SALWAR_PALAZZO",
                "template_name": "Women's Salwar / Trouser / Palazzo",
                "gender": "Women",
                "unit": "inch",
                "step_increment": Decimal("0.25"),
                "fields": [
                    {"name": "length", "label": "Outseam Length", "min": 30.0, "max": 48.0},
                    {"name": "waist", "label": "Waist", "min": 24.0, "max": 48.0},
                    {"name": "hip", "label": "Hip", "min": 30.0, "max": 56.0},
                    {"name": "thigh", "label": "Thigh Round", "min": 18.0, "max": 34.0},
                    {"name": "bottom_opening", "label": "Mori / Bottom Opening", "min": 10.0, "max": 26.0},
                    {"name": "crotch_depth", "label": "Crotch Depth", "min": 10.0, "max": 18.0}
                ],
                "directives": "Specify full/half elastic waist, side pocket, and ankle cut style."
            }
        ]

        # Remove legacy unstandardized template keys so only clean Men's & Women's matrices exist
        valid_types = [tmpl["garment_type"] for tmpl in measurement_templates]
        db.query(TailoringMeasurementTemplate).filter(
            ~TailoringMeasurementTemplate.garment_type.in_(valid_types)
        ).delete(synchronize_session=False)

        for tmpl in measurement_templates:
            existing_tmpl = db.query(TailoringMeasurementTemplate).filter_by(garment_type=tmpl["garment_type"]).first()
            if not existing_tmpl:
                t = TailoringMeasurementTemplate(
                    garment_type=tmpl["garment_type"],
                    display_title=tmpl["template_name"],
                    unit_default=tmpl["unit"],
                    step_increment=tmpl["step_increment"],
                    anchor_fields=json.dumps(tmpl["fields"]),
                    special_directives_placeholder=tmpl["directives"],
                    silhouette_icon=tmpl["gender"]
                )
                db.add(t)
            else:
                existing_tmpl.display_title = tmpl["template_name"]
                existing_tmpl.unit_default = tmpl["unit"]
                existing_tmpl.step_increment = tmpl["step_increment"]
                existing_tmpl.anchor_fields = json.dumps(tmpl["fields"])
                existing_tmpl.special_directives_placeholder = tmpl["directives"]
                existing_tmpl.silhouette_icon = tmpl["gender"]

        # 6. Seed GST Configuration (Official Registration)
        print("[Seed] Seeding GST Configurations...")
        gstin_val = "09AABCA1234F1Z8"
        existing_gst = db.query(GSTConfiguration).filter_by(gstin=gstin_val).first()
        if not existing_gst:
            g = GSTConfiguration(
                legal_name="AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers",
                trade_name="AASHIMA Atelier",
                gstin=gstin_val,
                state_code="09",
                state_name="Uttar Pradesh",
                address="581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India",
                is_composition=False,
                is_active=True
            )
            db.add(g)

        # 7. Seed Notification Templates (SMS & WhatsApp)
        print("[Seed] Seeding Notification Templates...")
        notification_templates = [
            (
                "BOOKING_CONFIRMATION",
                "Booking Intake Confirmation",
                "SMS",
                "AASHIMA: Namaste {customer_name}, your booking #{booking_number} ({garment_count} pcs) has been received. Expected Ready: {due_date}. Live Track: {tracking_url}"
            ),
            (
                "BOOKING_CONFIRMATION_WA",
                "WhatsApp Intake Dossier",
                "WhatsApp",
                "Namaste {customer_name} Ji,\n\nYour garments have been safely received at *AASHIMA Women's World & Stitchers 'N' Drapers*, 581 Turab Nagar.\n\n*Booking:* #{booking_number}\n*Total Garments:* {garment_count}\n*Estimated Handover:* {due_date}\n\nTrack your live artisan progress here:\n{tracking_url}\n\nThank you for choosing AASHIMA!"
            ),
            (
                "TRIAL_READY",
                "Garment Ready for Trial",
                "WhatsApp",
                "Namaste {customer_name} Ji,\nYour bespoke outfit #{booking_number} is ready for trial fitting at Turab Nagar counter. Kindly visit at your convenience."
            ),
            (
                "ORDER_COMPLETED",
                "Garment Ready for Handover",
                "WhatsApp",
                "Namaste {customer_name} Ji,\nYour order #{booking_number} is polished, steam finished, and ready for pickup at AASHIMA Turab Nagar. Balance payable: ₹{balance_due}."
            ),
            (
                "ORDER_DELIVERED",
                "Order Delivered & Closed",
                "SMS",
                "AASHIMA: Thank you {customer_name} for collecting booking #{booking_number}. Download your official GST Tax Invoice: {invoice_url}"
            )
        ]
        for code, name, ch, body in notification_templates:
            existing_nt = db.query(NotificationTemplate).filter_by(event_type=code).first()
            if not existing_nt:
                nt = NotificationTemplate(
                    event_type=code,
                    title=name,
                    channel=ch,
                    template_body=body,
                    is_active=True
                )
                db.add(nt)

        # 8. Seed Business Settings (Shop & Master Config)
        print("[Seed] Seeding Business Master Settings...")
        settings_data = [
            ("SHOP_NAME", "AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers", "string", "General", "Registered Business Name", True),
            ("SHOP_ADDRESS", "581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India", "string", "General", "Atelier Physical Counter Address", True),
            ("SHOP_PHONE", "+91 98102 44321", "string", "General", "Official Contact Hotline", True),
            ("SHOP_EMAIL", "care@aashima.in", "string", "General", "Support & Inquiries Email", True),
            ("SHOP_GSTIN", "09AABCA1234F1Z8", "string", "Taxation", "State GST Identification Number", True),
            ("SHOP_CURRENCY", "INR", "string", "General", "Operating Currency", True),
            ("SHOP_CURRENCY_SYMBOL", "₹", "string", "General", "Currency Display Symbol", True),
            ("SHOP_TYPE", "Single Shop Counter", "string", "General", "Business Model Setup", True),
            ("THERMAL_PRINTER_DEFAULT", "80mm ESC/POS", "string", "Hardware", "Standard Receipt Width", False),
            ("BLUETOOTH_PRINTING_ENABLED", "true", "boolean", "Hardware", "Enable Direct Bluetooth Tag Printing", False),
            ("SMS_NOTIFICATIONS_ENABLED", "true", "boolean", "Communication", "Send SMS for Intake and Delivery", False),
            ("WHATSAPP_NOTIFICATIONS_ENABLED", "true", "boolean", "Communication", "Send Rich WhatsApp Updates", False),
            ("DEFAULT_ADVANCE_PERCENTAGE", "30", "integer", "Billing", "Recommended advance on custom tailoring", False),
            ("INVOICE_PREFIX", "ASH-INV-2026-", "string", "Billing", "Tax Invoice Serial Prefix", False),
            ("BOOKING_PREFIX", "ASH-", "string", "Booking", "Booking Serial Prefix", False)
        ]
        for key, val, dt, cat, desc, pub in settings_data:
            existing_bs = db.query(BusinessSetting).filter_by(setting_key=key).first()
            if not existing_bs:
                bs = BusinessSetting(
                    setting_key=key,
                    setting_value=val,
                    data_type=dt,
                    category=cat,
                    description=desc,
                    is_public=pub
                )
                db.add(bs)

        db.commit()
        print("[Seed] Foundational setup complete: 0 synthetic customers, 0 synthetic orders. Ready for real operations!")
    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
