# AASHIMA ERP – Complete API Reference & Catalogue

**Base URL**: `http://localhost:8000/api/v1`  
**Interactive Swagger UI**: `http://localhost:8000/api/docs`  
**ReDoc Documentation**: `http://localhost:8000/api/redoc`  
**OpenAPI Specification**: `http://localhost:8000/api/openapi.json`  

---

## 1. Authentication & Security Guide

### 1.1 Staff & Owner Authentication
Staff and administrative users authenticate via `POST /api/v1/auth/login` using either their username or 10-digit registered phone number and password.

**Header Format**:
```http
Authorization: Bearer <jwt_access_token>
```

### 1.2 Customer OTP Authentication
Customers authenticate via a two-step phone OTP handshake:
1. `POST /api/v1/auth/customer/send-otp`: Sends a 6-digit OTP to the registered number.
2. `POST /api/v1/auth/customer/verify-otp`: Validates the OTP and returns a customer-scoped JWT token.

> [!IMPORTANT]
> Customer tokens have restricted scopes (`role: Customer`). Attempting to call internal administrative endpoints with a customer token results in an immediate `403 Forbidden` response.

---

## 2. API Endpoints Directory

### Group 1: Authentication & Identity
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Public | Staff/Owner login via username or phone |
| `POST` | `/api/v1/auth/refresh` | Public | Refresh token rotation |
| `POST` | `/api/v1/auth/customer/send-otp` | Public | Request 6-digit verification code |
| `POST` | `/api/v1/auth/customer/verify-otp` | Public | Verify OTP and issue customer JWT |
| `GET` | `/api/v1/auth/me` | Authenticated | Retrieve current user profile and role |

### Group 2: Customer Registry
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/v1/customers` | Staff, Owner | Search and filter customer dossiers |
| `POST` | `/api/v1/customers` | Staff, Owner | Register new customer with address |
| `GET` | `/api/v1/customers/{id}` | Staff, Owner | Get customer profile & past order stats |
| `PUT` | `/api/v1/customers/{id}` | Staff, Owner | Update patron tier, phone or unit |

### Group 3: Services & Fitting Blueprints
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/v1/services` | Public / Staff | List services by division (Women's World vs Stitchers) |
| `GET` | `/api/v1/services/templates/measurement` | Public / Staff | List Coat, Pant, Lehenga, Blouse templates |

### Group 4: Bookings & Garment Lifecycle
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/v1/bookings` | Staff, Owner | List all orders with filters (division, status, urgency) |
| `POST` | `/api/v1/bookings` | Staff, Owner | Create multi-garment booking with QR generation |
| `GET` | `/api/v1/bookings/{id}` | Staff, Owner | Retrieve full booking dossier, articles & history |
| `GET` | `/api/v1/garments/{id}` | Staff, Owner | Retrieve single garment article details |
| `POST` | `/api/v1/garments/{id}/transition` | Staff, Owner | Advance workflow stage with remarks and karigar |
| `POST` | `/api/v1/garments/{id}/photos` | Staff, Owner | Upload condition check / intake photo |
| `POST` | `/api/v1/garments/{id}/measurements`| Staff, Owner | Save 0.25in increment measurement matrix |

### Group 5: QR Code & Thermal Printing
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `POST` | `/api/v1/qr/scan` | Staff, Owner | Optical barcode scan, matches garment & logs history |
| `POST` | `/api/v1/qr/print-slips` | Staff, Owner | Generate 58mm/80mm ESC/POS and Base64 QR images |

### Group 6: Department Queues
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/v1/departments/alteration` | Staff, Owner | Active garments queued in Alteration wing |
| `GET` | `/api/v1/departments/deep-cleaning`| Staff, Owner | Active garments in Organic Dry Cleaning |
| `GET` | `/api/v1/departments/finishing` | Staff, Owner | Active garments in Steam Press & Polish |
| `GET` | `/api/v1/departments/delivery-centre`| Staff, Owner | Staged garments ready for pickup / dispatch |

### Group 7: Billing, Invoices & Daybook
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/v1/billing/daybook-summary` | Staff, Owner | Collected amounts, pending balance, cash vs UPI |
| `GET` | `/api/v1/billing/invoices` | Staff, Owner | List GST & Non-GST tax invoices |
| `POST` | `/api/v1/billing/invoices` | Staff, Owner | Generate tax invoice with CGST/SGST calculations |
| `GET` | `/api/v1/billing/invoices/{id}/pdf` | Public / Customer | Download official A4 Tax Invoice PDF |
| `GET` | `/api/v1/billing/payments` | Staff, Owner | Complete payment ledger entries |
| `POST` | `/api/v1/billing/payments` | Staff, Owner | Record advance, partial, or final payment |
| `GET` | `/api/v1/billing/expenses` | Accountant, Owner | List atelier operational expenses |
| `POST` | `/api/v1/billing/expenses` | Accountant, Owner | Log workshop expenditure voucher |

### Group 8: Transportation & Logistics
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/v1/deliveries` | Staff, Delivery | Scheduled store pickups and home deliveries |
| `POST` | `/api/v1/deliveries` | Staff, Delivery | Schedule delivery voucher with tracking ref |
| `POST` | `/api/v1/deliveries/{id}/updates` | Delivery, Owner | Add location update (e.g. In Transit, Out for Delivery) |
| `PUT` | `/api/v1/deliveries/{id}` | Delivery, Owner | Complete delivery and record POD |

### Group 9: Customer-Authenticated Tracking
| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/v1/public/track` | Verified Customer | Live tracking for the authenticated customer's own orders. Booking number, phone, or QR token alone is not authorization. |

---

## 3. Standard HTTP Status Codes

| Code | Meaning | Context |
|---|---|---|
| `200 OK` | Success | Standard GET/PUT successful response |
| `201 Created` | Resource Created | New customer, booking, invoice or payment recorded |
| `400 Bad Request` | Validation Error | Invalid payload, non-numeric price, or duplicate phone |
| `401 Unauthorized` | Auth Required | Missing or invalid Bearer JWT token |
| `403 Forbidden` | Access Denied | Customer attempting to access staff/admin endpoint |
| `404 Not Found` | Resource Missing | Booking number or QR token not found in database |
| `422 Unprocessable`| Pydantic Error | Field missing or data type mismatch |
| `500 Server Error` | Internal Failure | Unhandled database or operational exception |
