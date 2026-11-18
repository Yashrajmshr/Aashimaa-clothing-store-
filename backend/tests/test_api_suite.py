import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.seed_data import run_seed

@pytest.fixture(scope="module")
def client():
    # Ensure database is seeded with clean initial data
    run_seed()
    with TestClient(app) as c:
        yield c
    # Teardown: purge any transactional records created during tests
    run_seed()

def test_health_check(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "AASHIMA" in data["business"]

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
    assert "successfully dispatched" in res_send.json()["message"]
    assert "whatsapp_url" in res_send.json()

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

def test_customer_cannot_access_admin_api(client):
    # Obtain customer token
    verify_payload = {"phone": "9899001122", "otp": "123456"}
    customer_token = client.post("/api/v1/auth/customer/verify-otp", json=verify_payload).json()["access_token"]

    headers = {"Authorization": f"Bearer {customer_token}"}
    res = client.get("/api/v1/billing/daybook-summary", headers=headers)
    # Must be forbidden (403)
    assert res.status_code == 403

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
                "quantity": 1,
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

    # 6. Customer Live Public Tracking Check
    public_res = client.get(f"/api/v1/public/track?token={sec_token}")
    assert public_res.status_code == 200
    pub_data = public_res.json()
    assert pub_data["customer_name"] == "Smt. Meenakshi Sundaram"
    assert len(pub_data["timeline"]) == 5
    assert pub_data["billing"]["advance_paid"] == 1500.0

    # 7. Generate GST Tax Invoice
    inv_res = client.post("/api/v1/billing/invoices", json={"booking_id": booking_data["id"], "invoice_type": "GST"}, headers=headers)
    assert inv_res.status_code == 201
    inv_data = inv_res.json()
    assert inv_data["invoice_number"].startswith("ASH-INV-")
    assert Decimal(inv_data["cgst_amount"]) > 0

    # 8. Record Final Payment
    remaining = Decimal(inv_data["outstanding_balance"])
    if remaining > 0:
        pay_res = client.post("/api/v1/billing/payments", json={
            "booking_id": booking_data["id"],
            "amount": float(remaining),
            "payment_type": "Final",
            "payment_mode": "Cash"
        }, headers=headers)
        assert pay_res.status_code == 201
        pay_data = pay_res.json()
        assert pay_data["receipt"]["remaining_balance"] == "0.00"

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
