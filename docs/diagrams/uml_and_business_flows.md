# AASHIMA ERP – UML & Business Process Flow Diagrams

**Business**: AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers (581, Turab Nagar, Ghaziabad)  
**Standard**: UML 2.5 & BPMN 2.0 Representation in Mermaid  

---

## 1. Unified Modeling Language (UML) Diagrams

### 1.1 Use Case Diagram
```mermaid
flowchart LR
    subgraph Actors
        Owner["Owner / Manager"]
        Tailor["Master Karigar / Tailor"]
        Finisher["Steam Finishing Master"]
        Accountant["Chief Accountant"]
        DeliveryBoy["Delivery Personnel"]
        Customer["Boutique Patron"]
    end

    subgraph ERP["AASHIMA ERP System"]
        UC1["Create New Multi-Garment Booking"]
        UC2["Record 0.25in Tailoring Measurements"]
        UC3["Generate & Print 80mm QR Slips"]
        UC4["Scan Barcode & Update Floor Stage"]
        UC5["Inspect Quality & Enclose Archival"]
        UC6["Collect UPI / Cash & Generate Receipt"]
        UC7["Issue Official GST Tax Invoice"]
        UC8["Dispatch Order & Collect POD"]
        UC9["Live Track Garment via OTP"]
        UC10["Audit Financial Daybook & Ledger"]
    end

    Owner --> UC1
    Owner --> UC2
    Owner --> UC3
    Owner --> UC6
    Owner --> UC7
    Owner --> UC10

    Tailor --> UC2
    Tailor --> UC4
    Finisher --> UC4
    Finisher --> UC5

    Accountant --> UC6
    Accountant --> UC7
    Accountant --> UC10

    DeliveryBoy --> UC8

    Customer --> UC9
```

### 1.2 Sequence Diagram: New Multi-Garment Booking with QR Generation
```mermaid
sequenceDiagram
    autonumber
    actor Staff as Counter Staff (Android App)
    participant API as FastAPI Central Backend
    participant DB as PostgreSQL Database
    participant QR as QR Generator Engine
    participant Print as Bluetooth 80mm POS

    Staff->>API: POST /api/v1/bookings (Customer, Multi-Garments, Services, Advance)
    activate API
    API->>DB: Query customer patron tier & past dues
    API->>DB: Insert Booking (#ASH-8842)
    loop For each garment article
        API->>DB: Insert Garment (ASH-8842-G01)
        API->>QR: generate_secure_token("ASH-8842-G01")
        QR-->>API: Cryptographic token (HMAC-SHA256)
        API->>DB: Insert GarmentQRToken
        API->>DB: Insert Initial OrderStatusHistory (INTAKE)
    end
    API->>DB: Insert Payment & PaymentReceipt (Advance ₹1,000 via UPI)
    API->>DB: Commit Database Transaction
    API-->>Staff: Return 201 Created (Booking Dossier & QR Tokens)
    deactivate API

    Staff->>API: POST /api/v1/qr/print-slips (garment_ids, format="80mm")
    API->>QR: generate_thermal_slip_text() & generate_qr_data_uri()
    API-->>Staff: Return Base64 QR Image & ESC/POS Monospace Text
    Staff->>Print: Transmit via Bluetooth ESC/POS
    Print-->>Staff: Printed Adhesive Garment Claim Tag
```

### 1.3 State Machine Diagram: Garment Lifecycle
```mermaid
stateDiagram-v2
    [*] --> BookingReceived : Counter Intake & Inspection
    BookingReceived --> Alteration : Tailoring Cut / Resizing Needed
    BookingReceived --> DeepCleaning : Gentle Organic Care Needed
    BookingReceived --> Finishing : Finishing Only (Chiffon Press)

    Alteration --> DeepCleaning : Post-Tailoring Rinse
    Alteration --> Finishing : Fitting Alteration Completed

    DeepCleaning --> Finishing : Washed & Particulate Cleared

    Finishing --> DeliveryCentre : QC Passed & Archival Packaging
    DeliveryCentre --> ReadyForDelivery : Staged at 581 Turab Nagar Counter
    ReadyForDelivery --> OutForDelivery : Handed to Delivery Chauffeur
    ReadyForDelivery --> Delivered : Counter Handover (Claim Slip Verified)
    OutForDelivery --> Delivered : Customer Signed Proof-of-Delivery

    BookingReceived --> OnHold : Client Fabric Delay / Approval Needed
    OnHold --> BookingReceived : Client Approved
    BookingReceived --> Cancelled : Order Cancelled / Full Refund
    Delivered --> [*]
    Cancelled --> [*]
```

---

## 2. Business Process Flow Diagrams

### 2.1 Customer Booking & Garment Tagging Process
```mermaid
flowchart TD
    Start(["Customer Enters 581 Turab Nagar Counter"]) --> Lookup{"Existing Patron?"}
    Lookup -- Yes --> LoadDossier["Load Past Orders, Tier (Gold/Silver) & Fitting Archive"]
    Lookup -- No --> RegCust["Register New Patron Name, Mobile & Address"]

    LoadDossier --> SelectDiv["Select Business Division:<br/>AASHIMA Women's World or Stitchers 'N' Drapers"]
    RegCust --> SelectDiv

    SelectDiv --> AddArticles["Inspect & Add Garments:<br/>Type, Fabric, Color, Quantity"]
    AddArticles --> PhotoCheck{"Visible Flaw / Zari Condition?"}
    PhotoCheck -- Yes --> TakeMacroPhoto["Capture Macro Condition Photo (Intake Inspection)"]
    PhotoCheck -- No --> CheckMeas{"Tailoring Service Required?"}
    TakeMacroPhoto --> CheckMeas

    CheckMeas -- Yes --> OpenMatrix["Open Measurement Matrix (0.25in Precision Steppers)"]
    CheckMeas -- No --> CollectAdvance["Calculate Subtotal, 5% GST & Collect Advance"]
    OpenMatrix --> CollectAdvance

    CollectAdvance --> SaveOrder["FastAPI Generates Booking #ASH-XXXX and Unique QR Tokens"]
    SaveOrder --> PrintTag["Print 80mm ESC/POS Thermal Claim Slip & Barcode"]
    PrintTag --> AttachTag["Attach Barcode Tag to Garment Hanger / Protective Cover"]
    AttachTag --> HandSlip["Hand Claim Slip to Customer + Send WhatsApp Confirmation"]
    HandSlip --> End(["Garment Dispatched to Workshop Floor"])
```

### 2.2 QR Scanning & Floor Stage Update Process
```mermaid
flowchart TD
    ScanStart(["Artisan Receives Tagged Garment"]) --> OpenScanner["Open AASHIMA Android App Tag Scanner"]
    OpenScanner --> ScanOptical["Frame 80mm Tag in Camera Viewfinder"]
    ScanOptical --> DecodedToken["Decode Unpredictable HMAC Token"]
    DecodedToken --> APICall["FastAPI: POST /api/v1/qr/scan"]
    APICall --> FetchDossier["Load 100% Matched Customer, Article, Directives & Intake Photos"]
    FetchDossier --> SelectStage["Artisan Selects New Stage (e.g., Delicate Zari Steam Polish)"]
    SelectStage --> AssignKarigar["Select Karigar Name (Master Ramesh Chandra) & Enter Remarks"]
    AssignKarigar --> SubmitTransition["FastAPI: POST /api/v1/garments/{id}/transition"]
    SubmitTransition --> LogHistory["Append to Immutable order_status_history"]
    LogHistory --> PushNotif["Dispatch Automated SMS/WhatsApp Notification to Patron"]
    PushNotif --> LivePortal["Customer Live Tracking Reflects Updated Stage in Real-Time"]
    LivePortal --> EndScan(["Garment Advanced to Next Wing"])
```

### 2.3 Public Customer Tracking Flow (OTP Verified)
```mermaid
flowchart TD
    CustAccess(["Customer Visits aashima.in/track or Scans Tag QR"]) --> InputMethod{"Access Method?"}
    InputMethod -- "Scan Tag QR" --> DirectToken["Unpredictable Token Loaded from URL Parameter"]
    InputMethod -- "Manual Entry" --> EnterBooking["Enter Booking #ASH-8842 + Registered Mobile Number"]

    EnterBooking --> SendOTP["FastAPI: POST /api/v1/auth/customer/send-otp"]
    SendOTP --> PromptOTP["Customer Inputs 6-digit Mobile OTP"]
    PromptOTP --> VerifyOTP["FastAPI: POST /api/v1/auth/customer/verify-otp"]
    VerifyOTP -- Invalid --> RetryOTP["Display Error: Invalid/Expired OTP"]
    RetryOTP --> PromptOTP
    VerifyOTP -- Valid --> IssueToken["Issue Customer-Scoped JWT Token"]

    DirectToken --> LoadLive["FastAPI: GET /api/v1/public/track?token=..."]
    IssueToken --> LoadLive

    LoadLive --> RenderUI["Display 5-Stage Live Timeline with Pulsing Active Node"]
    RenderUI --> ShowProof["Show Macro Intake Photo Proof & Karigar Directives"]
    RenderUI --> ShowBill["Display Itemized Subtotal, Advance Paid & Balance Due"]
    ShowBill --> DownloadTaxPDF["Click 'Download Official Tax Invoice (PDF)'"]
    ShowBill --> ContactAtelier["One-Click WhatsApp / Phone Counter Assistance"]
    ContactAtelier --> FinishTrack(["Customer Informed with 100% Transparency"])
```
