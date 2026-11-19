import os
from pathlib import Path
from urllib.parse import urlsplit
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
tests_dir = Path(__file__).parent.resolve()
default_test_db = tests_dir / "aashima_disposable_test.db"

if os.getenv("AASHIMA_TESTING") != "1":
    os.environ["AASHIMA_TESTING"] = "1"
if os.getenv("ENVIRONMENT", "").lower() != "test":
    os.environ["ENVIRONMENT"] = "test"
if not os.getenv("DEFAULT_OTP_BYPASS"):
    os.environ["DEFAULT_OTP_BYPASS"] = "123456"
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = f"sqlite:///{default_test_db.as_posix()}"

test_database_url = os.getenv("DATABASE_URL", "")
if not test_database_url.startswith("sqlite:///") or not urlsplit(test_database_url).path.lower().endswith("_test.db"):
    raise RuntimeError("DATABASE_URL must point to a disposable SQLite file ending in _test.db")
test_database_path = Path(test_database_url[len("sqlite:///"):]).resolve()
if test_database_path.parent != tests_dir:
    raise RuntimeError("The disposable SQLite test database must live in backend/tests")

from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.services.seed_data import run_seed
from backend.app.models.auth import User, Role
from backend.app.core.security import get_password_hash
from backend.app.core.config import Settings
from scripts.backup_db import run_backup
from scripts.restore_db import restore_sqlite, verify_checksum

@pytest.fixture(scope="module")
def client():
    # Reset only the guarded disposable test database before each suite run.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    run_seed()
    with TestClient(app) as c:
        yield c
    # Never purge records in teardown. Each run must use a disposable test database.
    run_seed()

def test_health_check(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "AASHIMA" in data["business"]
    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}

def test_production_configuration_requires_a_real_otp_provider():
    base = {
        "_env_file": None,
        "ENVIRONMENT": "production",
        "PUBLIC_BASE_URL": "https://aashima.example",
        "DATABASE_URL": "postgresql://erp:strong-password@db/aashima_erp",
        "POSTGRES_PASSWORD": "strong-password",
        "SECRET_KEY": "production-only-secret-key-which-is-long-enough",
        "DEFAULT_OTP_BYPASS": None,
    }
    with pytest.raises(ValueError, match="supported real notification provider"):
        Settings(**base, NOTIFICATION_PROVIDER="mock")
    with pytest.raises(ValueError, match="FAST2SMS_API_KEY"):
        Settings(**base, NOTIFICATION_PROVIDER="fast2sms")
    configured = Settings(**base, NOTIFICATION_PROVIDER="fast2sms", FAST2SMS_API_KEY="test-provider-key")
    assert configured.ENVIRONMENT == "production"

def test_owner_login(client):
    payload = {
        "username_or_phone": "owner",
        "password": "Password@123"
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "Owner"
    assert data["full_name"] == "Aashima Singhal"

def test_customer_otp_flow(client):
    # 1. Login as owner to register a customer for this test
    owner_token = client.post("/api/v1/auth/login", json={"username_or_phone": "owner", "password": "Password@123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}
    
    test_phone = "9899001122"
    client.post("/api/v1/customers", json={
        "full_name": "Test Customer",
        "phone": test_phone,
        "email": "test@aashima.in",
        "patron_tier": "Silver Patron",
        "address": {"address_type": "Home", "address_line1": "Turab Nagar", "city": "Ghaziabad", "state": "UP", "pincode": "201001"}
    }, headers=headers)

    # 2. Send OTP
    send_payload = {"phone": test_phone}
    res_send = client.post("/api/v1/auth/customer/send-otp", json=send_payload)
    assert res_send.status_code == 200
    assert "If this number is registered" in res_send.json()["message"]
    assert "whatsapp_url" not in res_send.json()
    resend = client.post("/api/v1/auth/customer/send-otp", json=send_payload)
    unknown = client.post("/api/v1/auth/customer/send-otp", json={"phone": "9000000000"})
    assert resend.status_code == unknown.status_code == res_send.status_code
    assert resend.json() == unknown.json() == res_send.json()

    # 3. Verify OTP
    verify_payload = {
        "phone": test_phone,
        "otp": "123456" # Default test bypass OTP
    }
    res_verify = client.post("/api/v1/auth/customer/verify-otp", json=verify_payload)
    assert res_verify.status_code == 200
    data = res_verify.json()
    assert "access_token" in data
    assert data["customer_name"] == "Test Customer"

    locked_responses = [client.post("/api/v1/auth/customer/verify-otp", json={
        "phone": test_phone,
        "otp": "000000"
    }) for _ in range(6)]
    unknown_verify = client.post("/api/v1/auth/customer/verify-otp", json={
        "phone": "9000000000",
        "otp": "000000"
    })
    assert all(response.status_code == 400 for response in locked_responses)
    assert unknown_verify.status_code == 400
    assert all(response.json() == unknown_verify.json() for response in locked_responses)

def test_customer_cannot_access_admin_api(client):
    owner_token = client.post("/api/v1/auth/login", json={
        "username_or_phone": "owner", "password": "Password@123"
    }).json()["access_token"]
    customer_phone = "9899002233"
    created = client.post("/api/v1/customers", headers={"Authorization": f"Bearer {owner_token}"}, json={
        "full_name": "Admin Boundary Customer",
        "phone": customer_phone,
        "patron_tier": "Bronze"
    })
    assert created.status_code == 201
    verify_payload = {"phone": customer_phone, "otp": "123456"}
    customer_token = client.post("/api/v1/auth/customer/verify-otp", json=verify_payload).json()["access_token"]

    headers = {"Authorization": f"Bearer {customer_token}"}
    res = client.get("/api/v1/billing/daybook-summary", headers=headers)
    # Must be forbidden (403)
    assert res.status_code == 403

def test_staff_role_cannot_access_financial_or_business_settings(client):
    db = SessionLocal()
    try:
        staff_role = db.query(Role).filter(Role.name == "Staff").first()
        staff = User(
            username="floor_staff",
            email="floor_staff@test.invalid",
            full_name="Floor Staff",
            phone="9000000001",
            hashed_password=get_password_hash("FloorStaff@Test123"),
            is_active=True,
            is_verified=True
        )
        staff.roles.append(staff_role)
        db.add(staff)
        db.commit()
    finally:
        db.close()

    login = client.post("/api/v1/auth/login", json={
        "username_or_phone": "floor_staff",
        "password": "FloorStaff@Test123"
    })
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/v1/customers", headers=headers).status_code == 200
    assert client.get("/api/v1/billing/daybook-summary", headers=headers).status_code == 403
    assert client.get("/api/v1/settings", headers=headers).status_code == 403
    assert client.post("/api/v1/billing/payments", headers=headers, json={
        "booking_id": 1,
        "amount": 1,
        "payment_type": "Refund",
        "payment_mode": "Cash"
    }).status_code == 403
    assert client.post("/api/v1/billing/payments", headers=headers, json={
        "booking_id": 1,
        "amount": 1,
        "payment_type": "NotARealPayment",
        "payment_mode": "Cash"
    }).status_code == 422

def test_accountant_and_delivery_roles_have_separate_api_scopes(client):
    db = SessionLocal()
    try:
        accountant_role = db.query(Role).filter(Role.name == "Accountant").first()
        delivery_role = db.query(Role).filter(Role.name == "Delivery Staff").first()
        users = []
        for username, phone, role in [
            ("ledger_staff", "9000000002", accountant_role),
            ("dispatch_staff", "9000000003", delivery_role),
        ]:
            user = User(
                username=username,
                email=f"{username}@test.invalid",
                full_name=username,
                phone=phone,
                hashed_password=get_password_hash("ScopedRole@Test123"),
                is_active=True,
                is_verified=True
            )
            user.roles.append(role)
            db.add(user)
            users.append(user)
        db.commit()
    finally:
        db.close()

    accountant_login = client.post("/api/v1/auth/login", json={
        "username_or_phone": "ledger_staff", "password": "ScopedRole@Test123"
    })
    assert accountant_login.status_code == 200
    accountant_headers = {"Authorization": f"Bearer {accountant_login.json()['access_token']}"}
    assert client.get("/api/v1/billing/invoices", headers=accountant_headers).status_code == 200
    assert client.get("/api/v1/customers", headers=accountant_headers).status_code == 200
    assert client.post("/api/v1/customers", headers=accountant_headers, json={
        "full_name": "Should Be Denied", "phone": "9000000004", "patron_tier": "Bronze"
    }).status_code == 403

    delivery_login = client.post("/api/v1/auth/login", json={
        "username_or_phone": "dispatch_staff", "password": "ScopedRole@Test123"
    })
    assert delivery_login.status_code == 200
    delivery_headers = {"Authorization": f"Bearer {delivery_login.json()['access_token']}"}
    assert client.get("/api/v1/deliveries", headers=delivery_headers).status_code == 200
    assert client.get("/api/v1/billing/invoices", headers=delivery_headers).status_code == 403
    assert client.get("/api/v1/customers", headers=delivery_headers).status_code == 403

def test_create_customer_and_booking_with_multiple_garments(client):
    # 1. Login as owner
    owner_token = client.post("/api/v1/auth/login", json={"username_or_phone": "owner", "password": "Password@123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    # 2. Register customer
    new_phone = f"9871{Decimal('100000'):.0f}"
    cust_payload = {
        "full_name": "Smt. Meenakshi Sundaram",
        "phone": "9871998877",
        "email": "meenakshi@example.com",
        "patron_tier": "Gold Patron",
        "unit_reference": "Unit #C-04",
        "notes": "Bridal Trouseau client",
        "address": {
            "address_type": "Home",
            "address_line1": "Tower 2, Cloud 9, Vaishali",
            "city": "Ghaziabad",
            "state": "Uttar Pradesh",
            "pincode": "201010"
        }
    }
    cust_res = client.post("/api/v1/customers", json=cust_payload, headers=headers)
    assert cust_res.status_code in [201, 400] # 400 if already exists in test rerun
    if cust_res.status_code == 201:
        customer_id = cust_res.json()["id"]
    else:
        cust_list = client.get("/api/v1/customers?search=9871998877", headers=headers).json()
        customer_id = cust_list[0]["id"]

    # 3. Create Multi-Garment Booking
    # Get available services
    services = client.get("/api/v1/services", headers=headers).json()
    srv_ids = [s["id"] for s in services[:2]]

    invalid_booking = client.post("/api/v1/bookings", json={
        "customer_id": customer_id,
        "division": "AASHIMA Women's World",
        "delivery_due_date": "2026-11-25T18:00:00",
        "garments": [{"garment_name": "Invalid Service", "category": "Blouse", "service_ids": [999999]}]
    }, headers=headers)
    assert invalid_booking.status_code == 422

    booking_payload = {
        "customer_id": customer_id,
        "division": "AASHIMA Women's World",
        "order_type": "Bridal Atelier",
        "delivery_due_date": "2026-11-25T18:00:00",
        "trial_due_date": "2026-11-23T15:00:00",
        "is_urgent": True,
        "urgent_reason": "Wedding Reception",
        "notes": "Hand embroidery with gold zari thread",
        "advance_payment_amount": 1500.0,
        "advance_payment_mode": "UPI",
        "advance_transaction_id": "UPI-GPay-9871998877",
        "garments": [
            {
                "garment_name": "Bespoke Bridal Anarkali",
                "category": "Lehenga",
                "fabric_type": "Pure Georgette",
                "color": "Emerald Green",
                "quantity": 2,
                "rack_location": "Rack #C-02",
                "special_instructions": "Extra flair with can-can layering",
                "service_ids": [srv_ids[0]],
                "measurement": {
                    "template_garment_type": "LEHENGA_BLOUSE",
                    "unit": "INCH",
                    "measurements": {"bust": 38.0, "waist": 32.0, "length": 52.0},
                    "karigar_directives": "Deep back with latkans"
                }
            },
            {
                "garment_name": "Tissue Silk Dupatta",
                "category": "Saree",
                "fabric_type": "Tissue Silk",
                "color": "Muted Gold",
                "quantity": 1,
                "rack_location": "Rack #C-02",
                "service_ids": [srv_ids[1] if len(srv_ids) > 1 else srv_ids[0]]
            }
        ]
    }
    b_res = client.post("/api/v1/bookings", json=booking_payload, headers=headers)
    assert b_res.status_code == 201
    duplicate_advance = client.post("/api/v1/bookings", json=booking_payload, headers=headers)
    assert duplicate_advance.status_code == 409
    booking_data = b_res.json()
    assert len(booking_data["garments"]) == 2
    assert booking_data["advance_paid"] == "1500.00"
    garment1 = booking_data["garments"][0]
    garment1_id = garment1["id"]
    qr_ident = garment1["qr_code_identifier"]
    sec_token = garment1["secure_token"]

    # 4. QR Scan by Staff
    scan_res = client.post("/api/v1/qr/scan", json={"scanned_text": sec_token}, headers=headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["match_status"] == "100% Match"
    assert scan_data["customer_name"] == "Smt. Meenakshi Sundaram"

    # 5. Transition Garment Stage to Alteration
    trans_res = client.post(
        f"/api/v1/garments/{garment1_id}/transition",
        json={
            "new_stage": "Alteration",
            "remarks": "Assigned to Master Iqbal for can-can layering",
            "assigned_karigar_name": "Master Iqbal"
        },
        headers=headers
    )
    assert trans_res.status_code == 200
    assert trans_res.json()["current_stage"] == "Alteration"

    # 6. Customer tracking requires the verified customer session.
    public_url = f"/api/v1/public/track?token={sec_token}"
    assert client.get(public_url).status_code == 401
    client.post("/api/v1/auth/customer/send-otp", json={"phone": "9871998877"})
    customer_auth = client.post(
        "/api/v1/auth/customer/verify-otp",
        json={"phone": "9871998877", "otp": "123456"}
    )
    assert customer_auth.status_code == 200
    public_res = client.get(
        public_url,
        headers={"Authorization": f"Bearer {customer_auth.json()['access_token']}"}
    )
    assert public_res.status_code == 200
    pub_data = public_res.json()
    assert pub_data["customer_name"] == "Smt. Meenakshi Sundaram"
    assert len(pub_data["timeline"]) == 5
    assert pub_data["billing"]["advance_paid"] == 1500.0

    non_gst_booking = client.post("/api/v1/bookings", json={
        "customer_id": customer_id,
        "division": "AASHIMA Women's World",
        "order_type": "Counter",
        "delivery_due_date": "2026-11-25T18:00:00",
        "garments": [{"garment_name": "Non-GST Test Article", "category": "Blouse", "service_ids": [srv_ids[0]]}]
    }, headers=headers)
    assert non_gst_booking.status_code == 201
    non_gst_invoice = client.post("/api/v1/billing/invoices", json={
        "booking_id": non_gst_booking.json()["id"],
        "invoice_type": "Non-GST",
        "discount_amount": "50.00",
        "extra_charges": "25.00"
    }, headers=headers)
    assert non_gst_invoice.status_code == 201
    ng_data = non_gst_invoice.json()
    assert ng_data["invoice_type"] == "Non-GST"
    assert Decimal(ng_data["cgst_amount"]) == 0
    assert Decimal(ng_data["sgst_amount"]) == 0
    assert Decimal(ng_data["grand_total"]) == Decimal(ng_data["subtotal_amount"]) - Decimal("25.00")
    reconciled_booking = client.get(f"/api/v1/bookings/{non_gst_booking.json()['id']}", headers=headers).json()
    assert Decimal(reconciled_booking["net_amount"]) == Decimal(ng_data["grand_total"])
    assert Decimal(reconciled_booking["balance_due"]) == Decimal(ng_data["grand_total"])

    # 7. Generate GST Tax Invoice
    inv_res = client.post("/api/v1/billing/invoices", json={"booking_id": booking_data["id"], "invoice_type": "GST"}, headers=headers)
    assert inv_res.status_code == 201
    inv_data = inv_res.json()
    assert inv_data["invoice_number"].startswith("ASH-INV-")
    assert Decimal(inv_data["cgst_amount"]) > 0
    assert Decimal(inv_data["subtotal_amount"]) == Decimal(booking_data["total_amount"])
    assert Decimal(inv_data["grand_total"]) == Decimal(booking_data["net_amount"])

    customer_headers = {"Authorization": f"Bearer {customer_auth.json()['access_token']}"}
    customer_invoice_path = f"/api/v1/billing/invoices/{inv_data['id']}/customer-pdf"
    customer_invoice = client.get(customer_invoice_path, headers=customer_headers)
    assert customer_invoice.status_code == 200
    assert customer_invoice.headers["content-type"] == "application/pdf"
    assert customer_invoice.content.startswith(b"%PDF")
    initial_invoice_pdf = customer_invoice.content

    other_customer = client.post("/api/v1/customers", json={
        "full_name": "Other Customer",
        "phone": "9000000000",
        "patron_tier": "Bronze"
    }, headers=headers)
    assert other_customer.status_code == 201
    foreign_customer = client.post(
        "/api/v1/auth/customer/verify-otp",
        json={"phone": "9000000000", "otp": "123456"}
    )
    assert foreign_customer.status_code == 200
    foreign_headers = {"Authorization": f"Bearer {foreign_customer.json()['access_token']}"}
    assert client.get(customer_invoice_path, headers=foreign_headers).status_code == 404
    assert client.get(public_url, headers=foreign_headers).status_code == 404

    # 8. Record Final Payment
    remaining = Decimal(inv_data["outstanding_balance"])
    if remaining > 0:
        pay_res = client.post("/api/v1/billing/payments", json={
            "booking_id": booking_data["id"],
            "amount": float(remaining),
            "payment_type": "Final",
            "payment_mode": "Cash",
            "transaction_id": "FINAL-TEST-001"
        }, headers=headers)
        assert pay_res.status_code == 201
        pay_data = pay_res.json()
        assert pay_data["receipt"]["remaining_balance"] == "0.00"
        retry = client.post("/api/v1/billing/payments", json={
            "booking_id": booking_data["id"],
            "amount": float(remaining),
            "payment_type": "Final",
            "payment_mode": "Cash",
            "transaction_id": "FINAL-TEST-001"
        }, headers=headers)
        assert retry.status_code == 201
        assert retry.json()["id"] == pay_data["id"]
        reused = client.post("/api/v1/billing/payments", json={
            "booking_id": booking_data["id"],
            "amount": 1,
            "payment_type": "Partial",
            "payment_mode": "Cash",
            "transaction_id": "FINAL-TEST-001"
        }, headers=headers)
        assert reused.status_code == 409

    refund_res = client.post("/api/v1/billing/payments", json={
        "booking_id": booking_data["id"],
        "amount": 100,
        "payment_type": "Refund",
        "payment_mode": "UPI",
        "transaction_id": "REFUND-TEST-001"
    }, headers=headers)
    assert refund_res.status_code == 201
    assert refund_res.json()["payment_type"] == "Refund"
    assert refund_res.json()["receipt"]["remaining_balance"] == "100.00"
    updated_customer_invoice = client.get(customer_invoice_path, headers=customer_headers)
    assert updated_customer_invoice.status_code == 200
    assert updated_customer_invoice.content != initial_invoice_pdf

    # 9. Verify and Test Invoice Deletion
    del_inv = client.delete(f"/api/v1/billing/invoices/{inv_data['id']}", headers=headers)
    assert del_inv.status_code == 200
    assert "deleted successfully" in del_inv.json()["message"]

def test_delete_booking_and_customer(client):
    owner_token = client.post("/api/v1/auth/login", json={"username_or_phone": "owner", "password": "Password@123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    # 1. Create a customer
    cust_res = client.post("/api/v1/customers", json={
        "full_name": "Delete Test Patron",
        "phone": "9998887766",
        "patron_tier": "Bronze"
    }, headers=headers)
    assert cust_res.status_code == 201
    cust_id = cust_res.json()["id"]

    # 2. Get services
    srvs = client.get("/api/v1/services", headers=headers).json()
    srv_id = srvs[0]["id"]

    # 3. Create a booking
    book_res = client.post("/api/v1/bookings", json={
        "customer_id": cust_id,
        "division": "AASHIMA Women's World",
        "order_type": "Counter",
        "delivery_due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
        "is_urgent": False,
        "advance_payment_amount": 100,
        "garments": [{
            "garment_name": "Test Lehenga to Delete",
            "category": "Lehenga",
            "service_ids": [srv_id]
        }]
    }, headers=headers)
    assert book_res.status_code == 201
    booking_id = book_res.json()["id"]

    # 4. Delete the booking
    del_book_res = client.delete(f"/api/v1/bookings/{booking_id}", headers=headers)
    assert del_book_res.status_code == 200
    assert "deleted successfully" in del_book_res.json()["message"]

    # 5. Verify booking is hidden from list
    list_res = client.get("/api/v1/bookings", headers=headers).json()
    assert not any(b["id"] == booking_id for b in list_res)

    # 6. Delete the customer
    del_cust_res = client.delete(f"/api/v1/customers/{cust_id}", headers=headers)
    assert del_cust_res.status_code == 200
    assert "deleted successfully" in del_cust_res.json()["message"]

    # 7. Verify customer is hidden from list
    cust_list = client.get("/api/v1/customers", headers=headers).json()
    assert not any(c["id"] == cust_id for c in cust_list)

def test_sqlite_backup_restores_only_to_a_new_verified_target(client, tmp_path):
    archive = run_backup(tmp_path)
    verify_checksum(archive, allow_legacy=False)
    restored_path = restore_sqlite(archive, tmp_path / "restored_test.db")
    import sqlite3
    with sqlite3.connect(restored_path) as restored:
        assert restored.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert restored.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0
    with pytest.raises(FileExistsError, match="never overwrites"):
        restore_sqlite(archive, restored_path)
