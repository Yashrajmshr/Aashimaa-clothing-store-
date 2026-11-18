# AASHIMA ERP – Standard Operating Procedures (SOP Manual)

**Business Entity**: AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers  
**Location**: 581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India  
**Applicability**: All Atelier Staff, Karigars, Store Managers, Accountants, Delivery Staff  
**Document Ref**: SOP-AASHIMA-2026-V2.4  

---

## Index of Standard Operating Procedures

- **SOP-001**: Owner Login and Dashboard Management
- **SOP-002**: New Customer Registration
- **SOP-003**: New Booking Entry
- **SOP-004**: Garment Inspection and Photograph Upload
- **SOP-005**: Tailoring Measurement Entry
- **SOP-006**: QR Generation and Garment Tag Printing
- **SOP-007**: Garment Receiving and Department Assignment
- **SOP-008**: Alteration Department Workflow
- **SOP-009**: Deep Cleaning Workflow
- **SOP-010**: Finishing and Quality Inspection
- **SOP-011**: Delivery Centre Management
- **SOP-012**: QR-Based Garment Status Updates
- **SOP-013**: Advance and Partial Payment Collection
- **SOP-014**: GST and Non-GST Invoice Generation
- **SOP-015**: Customer Tracking and OTP Verification
- **SOP-016**: Transportation and Delivery Confirmation
- **SOP-017**: Refund and Cancellation Handling
- **SOP-018**: Daily Closing and Financial Reconciliation
- **SOP-019**: Staff Access Management
- **SOP-020**: Data Backup and Recovery

---

### SOP-001: Owner Login and Dashboard Management
- **SOP ID**: SOP-001
- **Title**: Owner Login and Dashboard Management
- **Purpose**: Authenticate administrative authority and review shop floor positions, financial daybook, and critical delivery alerts.
- **Scope**: Counter Terminal and Executive Mobile Devices.
- **Responsible Person**: Business Owner / Store Manager.
- **Prerequisites**: Active operator credentials in `users` database.
- **Step-by-Step Instructions**:
  1. Launch the AASHIMA Android App or navigate to `admin.aashima.in`.
  2. Input registered username (`owner` or `9810244321`) and secure password.
  3. Tap **Open Atelier Counter**.
  4. Review top-level KPIs: Gross Daybook Collection, Live Pipeline Pieces (124 in floor), and Urgent Flags.
  5. Inspect the Critical Deliveries widget for bridal orders due within 90 minutes.
- **Expected Result**: System unlocks shift operations and displays real-time counter metrics.
- **Exception Handling**: If password authentication fails three times, account enters a 10-minute cooldown.
- **Security Considerations**: Never share owner credentials with tailors or karigars; enforce screen auto-lock.
- **Records Maintained**: `staff_activity` and `audit_logs` record login timestamp, IP address, and device agent.

---

### SOP-002: New Customer Registration
- **SOP ID**: SOP-002
- **Title**: New Customer Registration
- **Purpose**: Enroll boutique clients into the centralized patron registry with contact, address, and tier metadata.
- **Scope**: Turab Nagar intake counter.
- **Responsible Person**: Counter Front Desk Operator.
- **Prerequisites**: Client phone number verification.
- **Step-by-Step Instructions**:
  1. Search for customer mobile number using the global search toolbar.
  2. If not found, tap **New Patron Registration**.
  3. Enter Customer Full Name (e.g. Smt. Sunita Sharma).
  4. Enter 10-digit mobile number and optional email.
  5. Assign initial Patron Tier (`Standard`, `Silver`, or `Gold Patron` based on profile).
  6. Enter delivery address (House/Flat, Street, Landmark, City, Pincode).
  7. Add Unit Reference if applicable (e.g. `Unit #B-14`).
  8. Save record to generate unique identifier (`CUST-XXXX`).
- **Expected Result**: Customer created with zero initial balance and ready for booking linkage.
- **Exception Handling**: If mobile number already exists, system displays existing profile with past order history.
- **Security Considerations**: Phone number is encrypted in transit; never expose client address publicly.
- **Records Maintained**: `customers` and `customer_addresses` tables.

---

### SOP-003: New Booking Entry
- **SOP ID**: SOP-003
- **Title**: New Multi-Garment Booking Entry
- **Purpose**: Record client articles, attach requested services, calculate prices, and set expected trial/delivery dates.
- **Scope**: Counter POS intake.
- **Responsible Person**: Counter Staff / Store Manager.
- **Prerequisites**: Customer record must exist (SOP-002).
- **Step-by-Step Instructions**:
  1. Open **New Order** form.
  2. Select Customer from registry.
  3. Choose Business Division: `AASHIMA Women's World` (Bridal/Care) or `AASHIMA Stitchers 'N' Drapers` (Suits/Kurta).
  4. For each article received:
     - Input article name (e.g. Pure Kanjeevaram Saree, Heavy Bridal Lehenga).
     - Select fabric (Pure Silk, Velvet, Georgette) and color.
     - Select services from catalog (Deep Cleaning, Alteration, Zari Polish, Tailoring).
  5. If tailoring is required, toggle **Link Measurements Matrix** (SOP-005).
  6. Set Expected Delivery Date and Trial Fitting Date.
  7. Toggle **Urgent Handover** checkbox if required (e.g. Bridal Reception).
  8. Enter advance payment collected (SOP-013).
  9. Tap **Generate QR & Save Booking**.
- **Expected Result**: Booking voucher created (`#ASH-XXXX`), unique garment tags (`ASH-XXXX-G01`) generated.
- **Exception Handling**: Order cannot be saved without at least one valid garment article.
- **Security Considerations**: Financial amounts are computed via backend Decimal precision; zero client tampering.
- **Records Maintained**: `bookings`, `garments`, `booking_services` tables.

---

### SOP-004: Garment Inspection and Photograph Upload
- **SOP ID**: SOP-004
- **Title**: Garment Inspection and Photograph Upload
- **Purpose**: Document pre-existing garment flaws, zari pulls, stains, or delicate embroidery conditions prior to workshop handoff.
- **Scope**: Counter inspection lighting station.
- **Responsible Person**: Inspection Staff / Karigar.
- **Prerequisites**: Booking voucher generated (SOP-003).
- **Step-by-Step Instructions**:
  1. Place garment on inspection table under balanced 5500K daylight lighting.
  2. Inspect pallu border, neckline, armholes, and hem for tears or color bleeding.
  3. Open AASHIMA App, tap **Intake Photo Proof** on the garment card.
  4. Capture clear macro shot of the critical embroidery or flaw (e.g. Pallu Border Check).
  5. Add caption: "Verified client gold weave condition notes recorded."
  6. Tap **Upload Proof** to save to media archive.
- **Expected Result**: Photographic proof linked to garment record and visible in customer live tracking portal.
- **Exception Handling**: If camera is unavailable, record written condition notes in the `defect_notes` field.
- **Security Considerations**: Photos are stored under private hashes preventing unauthenticated directory browsing.
- **Records Maintained**: `garment_photographs` table.

---

### SOP-005: Tailoring Measurement Entry
- **SOP ID**: SOP-005
- **Title**: Tailoring Measurement Entry
- **Purpose**: Record precise physical body measurements for bespoke bridal and suit tailoring.
- **Scope**: Private fitting salon / measurement area.
- **Responsible Person**: Master Tailor / Fitting Consultant.
- **Prerequisites**: Customer present; measuring tape calibrated.
- **Step-by-Step Instructions**:
  1. Open **Measurement Book** on tablet POS.
  2. Select Garment Segment: `COAT`, `PANT`, `SHIRT`, `KURTA_PAJAMA`, or `LEHENGA_BLOUSE`.
  3. Select Unit: `INCH (")` or `CM`.
  4. If client has past fitting records, tap **Load May 2023 Fitting Archive** for baseline comparison.
  5. Use 0.25" increment steppers (+ / -) to record all 10 anchor measurements:
     - Blouse Length, Bust, Under Bust, Front Neck Depth, Back Neck Depth, Sleeve Length, Armhole, Lehenga Length, Waist, Flare.
  6. Input Special Karigar Directives: "Add 1.5 inch margin in sides, deep neckline with handcrafted latkans."
  7. Tap **Save Measurements to Article**.
- **Expected Result**: Precision matrix attached to garment code and transmitted to Master Iqbal station.
- **Exception Handling**: Warning flagged if bust-to-waist ratio exceeds anatomical standard bounds.
- **Security Considerations**: Client measurement records are confidential and restricted from public view.
- **Records Maintained**: `garment_measurements` table.

---

### SOP-006: QR Generation and Garment Tag Printing
- **SOP ID**: SOP-006
- **Title**: QR Generation and Garment Tag Printing
- **Purpose**: Print machine-scannable adhesive thermal tags and client claim slips.
- **Scope**: Counter POS printer station.
- **Responsible Person**: Counter Operator.
- **Prerequisites**: Paired Bluetooth 80mm or 58mm ESC/POS printer.
- **Step-by-Step Instructions**:
  1. Open booking confirmation screen.
  2. Verify Bluetooth printer status indicator shows **Bluetooth 80mm Active**.
  3. Select print layout: `80mm ESC/POS Roll`.
  4. Tap **Print Slip**.
  5. The printer outputs:
     - Header: AASHIMA Atelier, Turab Nagar, Phone.
     - Barcode: Machine-readable 200px QR token.
     - Human-readable: Tag ID (`ASH-8842-G01`), Rack (`Rack #B-14`), Booking (`#ASH-8842`).
     - Client Name, phone, and unit reference.
     - Perforated Claim Slip with tear line for customer handover.
  6. Securely staple tag to garment hanger / protective polybag.
- **Expected Result**: Physical tag attached to garment; print log recorded.
- **Exception Handling**: If thermal printer runs out of paper, re-trigger via **Reprint Tag** button.
- **Security Considerations**: Public QR payload contains only unpredictable cryptographic hash, zero PII.
- **Records Maintained**: `garment_qr_tokens` and print counters.

---

### SOP-007: Garment Receiving and Department Assignment
- **SOP ID**: SOP-007
- **Title**: Garment Receiving and Department Assignment
- **Purpose**: Hand over tagged garments from front counter to workshop floor wings.
- **Scope**: Workshop intake staging zone.
- **Responsible Person**: Floor Manager / Intake Coordinator.
- **Prerequisites**: Tag attached (SOP-006).
- **Step-by-Step Instructions**:
  1. Floor coordinator scans tag barcode using Android App scanner.
  2. App confirms 100% Match and displays required services.
  3. Allocate garment to initial department:
     - If tailoring/alteration required -> Route to Alteration Wing (Master Iqbal).
     - If dry clean only -> Route to Organic Deep Cleaning Wing.
     - If finishing only -> Route to Steam Press Station.
  4. Place garment in designated station rack (e.g. `Station #2`).
  5. Update status to initial processing stage.
- **Expected Result**: Garment appears in appropriate department work queue.
- **Exception Handling**: Unrecognized tags must be held at intake until booking voucher is verified.
- **Security Considerations**: Scan timestamp and user ID are recorded for chain-of-custody.
- **Records Maintained**: `department_assignments` and `order_status_history`.

---

### SOP-008: Alteration Department Workflow
- **SOP ID**: SOP-008
- **Title**: Alteration Department Workflow
- **Purpose**: Execute resizing, dart adjustments, hem stitching, and karigari embroidery repairs.
- **Scope**: Alteration Workshop Wing.
- **Responsible Person**: Master Tailor (Master Iqbal).
- **Prerequisites**: Garment queued in Alteration (SOP-007).
- **Step-by-Step Instructions**:
  1. Open Alteration Queue on workshop tablet.
  2. Select order and view karigar directives and measurement specs.
  3. Execute physical alterations on industrial sewing/overlock machines.
  4. Check seam margins and reinforce latkan loops or hooks.
  5. Upon completion, scan garment QR code.
  6. Select next stage: `Finishing` or `Deep Cleaning`.
  7. Input remarks: "Alteration completed by Master Iqbal. Ready for steam press."
  8. Tap **Complete Stage Transition**.
- **Expected Result**: Status advances; notification dispatched to client; order moves to finishing queue.
- **Exception Handling**: If fabric is insufficient for margin expansion, set stage to `On Hold` and flag owner.
- **Security Considerations**: Only staff with `garment:stage_update` permission can approve completion.
- **Records Maintained**: `order_status_history`.

---

### SOP-009: Deep Cleaning Workflow
- **SOP ID**: SOP-009
- **Title**: Deep Cleaning Workflow
- **Purpose**: Execute pH-balanced dry cleaning, stain spot treatment, and particulate removal.
- **Scope**: Dry Cleaning & Washing Plant.
- **Responsible Person**: Wash Master / Plant Technician.
- **Prerequisites**: Garment received in Deep Cleaning queue.
- **Step-by-Step Instructions**:
  1. Verify fabric care label and client condition notes.
  2. Treat collar, cuff, and pallu stains with specialized organic spotting agents.
  3. Process delicate silk garments in hydrocarbon dry-cleaning drum at controlled temperature.
  4. Deodorize and dry under regulated air cycle.
  5. Inspect for complete stain removal.
  6. Scan garment QR tag in AASHIMA App.
  7. Select next stage: `Finishing`.
  8. Enter remarks: "Purified pH-balanced mild silk emulsion rinse and particulate removal completed."
  9. Tap **Complete Stage Transition**.
- **Expected Result**: Garment cleaned, sanitized, and advanced to steam finishing.
- **Exception Handling**: Stubborn stains requiring chemical re-treatment must be documented before second cycle.
- **Security Considerations**: Chemical handling must follow atelier safety protocols.
- **Records Maintained**: `order_status_history`.

---

### SOP-010: Finishing and Quality Inspection
- **SOP ID**: SOP-010
- **Title**: Finishing and Quality Inspection
- **Purpose**: Execute specialized temperature-regulated steam form pressing, zari luster polishing, and final QC.
- **Scope**: Finishing Station.
- **Responsible Person**: Finishing Master (Master Ramesh Chandra) & QC Inspector.
- **Prerequisites**: Garment received in Finishing queue.
- **Step-by-Step Instructions**:
  1. Position garment on vacuum steam table / mannequin form.
  2. Apply regulated steam press avoiding direct iron contact on zari work.
  3. Polish metallic embroidery threads with velvet buffering cloth.
  4. Perform 5-point Quality Check:
     - Stitch density & thread trims.
     - Measurement adherence to ticket.
     - Zari luster & absence of scorch marks.
     - Hem alignment and hook strength.
     - Overall presentation.
  5. Enclose garment in breathable heirloom archival garment bag.
  6. Scan QR code and advance stage to `Delivery Centre Staged`.
  7. Add remarks: "Signed by Master Ramesh Chandra. QC Passed."
- **Expected Result**: Garment packaged, verified, and staged for customer trial / pickup.
- **Exception Handling**: Garments failing QC are routed back to Alteration or Finishing with defect notes.
- **Security Considerations**: QC stamp requires authenticated staff PIN.
- **Records Maintained**: `order_status_history` with QC signoff.

---

### SOP-011: Delivery Centre Management
- **SOP ID**: SOP-011
- **Title**: Delivery Centre Management
- **Purpose**: Stage inspected bridal garments on organized pickup racks and manage counter handovers.
- **Scope**: 581 Turab Nagar Delivery Staging Bay.
- **Responsible Person**: Delivery Supervisor / Counter Staff.
- **Prerequisites**: Garment stage is `Delivery Centre Staged`.
- **Step-by-Step Instructions**:
  1. Place packaged garment in assigned rack slot (e.g. `Rack #B-14`).
  2. Verify all multi-article garments of the booking are assembled together.
  3. When all articles are present, system automatically marks booking as `Ready for Delivery`.
  4. System dispatches automated SMS & WhatsApp notification: "Namaste! Your garment is Ready for Trial at 581 Turab Nagar."
  5. Ensure physical claim slip is ready at the pickup register.
- **Expected Result**: Booking marked `Ready for Delivery`; customer alerted with balance due amount.
- **Exception Handling**: Missing sibling articles prevent booking status from advancing to `Ready for Delivery`.
- **Security Considerations**: Garments can only be released upon presentation of physical claim slip or OTP.
- **Records Maintained**: `deliveries` and `bookings` status tables.

---

### SOP-012: QR-Based Garment Status Updates
- **SOP ID**: SOP-012
- **Title**: QR-Based Garment Status Updates
- **Purpose**: Maintain zero-latency status tracking across workshop floor using barcode scans.
- **Scope**: All mobile and tablet scanning stations.
- **Responsible Person**: All workshop artisans.
- **Prerequisites**: Mobile App installed and logged in.
- **Step-by-Step Instructions**:
  1. Tap center elevated **Scan Tag** button in bottom navigation.
  2. Align camera viewfinder with the 80mm thermal QR tag.
  3. Upon barcode detection, app plays success chime and opens **Garment Dossier**.
  4. Verify matching client name and garment title.
  5. Tap target stage pill (e.g. `Finishing`, `Ready for Delivery`).
  6. Tap **Complete Stage Transition**.
- **Expected Result**: Transition committed to PostgreSQL; customer website updates within 1 second.
- **Exception Handling**: If camera fails, enter numerical tag code manually in fallback field.
- **Security Considerations**: Barcode tokens are cryptographically signed preventing brute-force stage forgery.
- **Records Maintained**: `qr_scan_history` and `order_status_history`.

---

### SOP-013: Advance and Partial Payment Collection
- **SOP ID**: SOP-013
- **Title**: Advance and Partial Payment Collection
- **Purpose**: Collect booking advances or balance dues via UPI, Cash, or Card, maintaining an exact daybook ledger.
- **Scope**: Cash counter and POS terminal.
- **Responsible Person**: Cashier / Counter Operator / Accountant.
- **Prerequisites**: Active booking with pending balance.
- **Step-by-Step Instructions**:
  1. Open **Collect Payment** screen in mobile app or admin dashboard.
  2. Search for order # or scan garment claim tag.
  3. System displays Net Payable, Advance Paid, and Remaining Balance Due.
  4. Enter payment amount collected.
  5. Select payment mode: `UPI`, `Cash`, or `Card`.
  6. For UPI, confirm settlement on shop soundbox / UPI terminal and record UTR reference.
  7. Tap **Generate Receipt & Settle**.
  8. Hand printed receipt (`REC-YYYY-XXXX`) to client.
- **Expected Result**: `payments` record inserted, booking balance deducted, and customer outstanding dues reduced.
- **Exception Handling**: Split payments (part cash, part UPI) must be entered as two distinct transactions.
- **Security Considerations**: Cash amounts must be reconciled against drawer balance at shift close.
- **Records Maintained**: `payments`, `payment_receipts`, and `bookings.advance_paid`.

---

### SOP-014: GST and Non-GST Invoice Generation
- **SOP ID**: SOP-014
- **Title**: GST and Non-GST Invoice Generation
- **Purpose**: Generate legally compliant GST tax invoices with exact HSN/SAC breakdowns.
- **Scope**: Accounts department & counter terminal.
- **Responsible Person**: Chief Accountant (Rohan Sharma) / Owner.
- **Prerequisites**: Booking completed or billed.
- **Step-by-Step Instructions**:
  1. Navigate to **GST Invoicing & Ledger** in Admin Web Portal.
  2. Select Booking `#ASH-XXXX`.
  3. Choose Invoice Type: `GST Tax Invoice` (Default) or `Non-GST Invoice`.
  4. System computes:
     - Taxable Value of Tailoring (SAC 998822) @ 5% GST (2.5% CGST + 2.5% SGST).
     - Taxable Value of Dry Cleaning (SAC 999712) @ 18% GST (9% CGST + 9% SGST).
     - Grand Total, Paid Amount, and Balance Due.
  5. Tap **Generate Tax Invoice**.
  6. Download or print the official A4 PDF invoice.
- **Expected Result**: Permanent invoice generated (`ASH-INV-YYYY-XXXX`) with downloadable PDF.
- **Exception Handling**: Price discounts must be approved by Store Manager before invoice locking.
- **Security Considerations**: Once generated, invoice numbers cannot be deleted or re-used (GST compliant).
- **Records Maintained**: `invoices` and `invoice_items` tables.

---

### SOP-015: Customer Tracking and OTP Verification
- **SOP ID**: SOP-015
- **Title**: Customer Tracking and OTP Verification
- **Purpose**: Enable clients to track garment progress securely without exposing private contact info.
- **Scope**: Customer web portal (`aashima.in/track`).
- **Responsible Person**: Customer / Support Staff.
- **Prerequisites**: Internet-connected browser on smartphone or PC.
- **Step-by-Step Instructions**:
  1. Patron navigates to `aashima.in/track` or scans garment QR tag.
  2. Enter Booking Number (`#ASH-8842`) and registered mobile number.
  3. Tap **Send Verification OTP**.
  4. System sends a 6-digit OTP via SMS / WhatsApp.
  5. Input the 6-digit code on the portal and tap **Verify & View Live Status**.
  6. Client reviews:
     - 5-stage live status tracker with pulsing node.
     - Intake macro photo proof.
     - Itemized bill, advance paid, and remaining balance.
     - Download official Tax Invoice (PDF).
- **Expected Result**: Secure read-only access granted for the verified customer session.
- **Exception Handling**: In development / test mode, code `123456` bypasses external SMS gateway.
- **Security Considerations**: Customer session token cannot perform administrative operations.
- **Records Maintained**: Customer OTP attempts and token issuance logs.

---

### SOP-016: Transportation and Delivery Confirmation
- **SOP ID**: SOP-016
- **Title**: Transportation and Delivery Confirmation
- **Purpose**: Manage out-for-delivery orders and record proof of delivery (POD).
- **Scope**: Delivery fleet and logistics counter.
- **Responsible Person**: Delivery Personnel (Sunil Kumar) / Chauffeur.
- **Prerequisites**: Order staged at delivery centre.
- **Step-by-Step Instructions**:
  1. Delivery staff receives packaged garment with delivery voucher.
  2. Update delivery status to `Out for Delivery`.
  3. Transport garment in dust-proof wardrobe van to client address.
  4. At client doorstep, request verified claim slip or inspect handover code.
  5. Collect remaining balance dues via UPI / Cash (SOP-013).
  6. Have client sign the physical delivery manifest or capture photo POD.
  7. In App, tap **Confirm Handover / Delivered**.
- **Expected Result**: Order marked `Delivered`; customer receive delivery receipt.
- **Exception Handling**: If client is unavailable, record `Failed Attempt` and reschedule for next day.
- **Security Considerations**: High-value bridal garments require signed physical POD.
- **Records Maintained**: `deliveries` and `transportation_updates` tables.

---

### SOP-017: Refund and Cancellation Handling
- **SOP ID**: SOP-017
- **Title**: Refund and Cancellation Handling
- **Purpose**: Process customer order cancellations, fabric returns, and advance refunds with audit traceability.
- **Scope**: Accounts and store management.
- **Responsible Person**: Business Owner / Store Manager.
- **Prerequisites**: Booking status must be prior to `Finishing`.
- **Step-by-Step Instructions**:
  1. Open booking record in Admin Web Portal.
  2. Review current stage and accumulated artisan labor costs.
  3. If approved for cancellation, select stage: `Cancelled`.
  4. Input formal cancellation reason in remarks.
  5. Record refund payment transaction with negative or refund classification.
  6. Return client unworked fabric or garments with handover receipt.
  7. Update customer account dues ledger.
- **Expected Result**: Booking cancelled, payment ledger reconciled, and customer notified.
- **Exception Handling**: Once a garment reaches `Finishing` or `QC Passed`, cancellations are non-refundable.
- **Security Considerations**: All cancellations require Owner PIN authorization.
- **Records Maintained**: `audit_logs` and `payments` tables.

---

### SOP-018: Daily Closing and Financial Reconciliation
- **SOP ID**: SOP-018
- **Title**: Daily Closing and Financial Reconciliation
- **Purpose**: Reconcile daily counter cash, UPI settlements, slips billed, and shift closing ledger.
- **Scope**: 581 Turab Nagar front desk.
- **Responsible Person**: Chief Accountant & Store Manager.
- **Prerequisites**: End of operational business day (9:00 PM).
- **Step-by-Step Instructions**:
  1. Navigate to **Daybook Ledger** on Admin Web Portal.
  2. Run daily summary for current date.
  3. Verify:
     - Cash collected matches physical cash in register drawer.
     - UPI collections match bank account credits.
     - Total slips billed count matches intake physical vouchers.
  4. Record daybook closing position.
  5. Print daily closing statement and deposit cash into atelier safe.
- **Expected Result**: Counter daybook verified with zero reconciliation discrepancy.
- **Exception Handling**: Any discrepancy exceeding ₹100 must be investigated via `staff_activity` logs.
- **Security Considerations**: Daily financial summaries are restricted to Owner and Accountant roles.
- **Records Maintained**: `payments`, `expenses`, and `audit_logs` tables.

---

### SOP-019: Staff Access Management
- **SOP ID**: SOP-019
- **Title**: Staff Access Management
- **Purpose**: Provision and revoke staff logins, assign workshop roles, and enforce security policies.
- **Scope**: Atelier IT and management administration.
- **Responsible Person**: Business Owner.
- **Prerequisites**: New employee contract signed.
- **Step-by-Step Instructions**:
  1. Open **Atelier Settings -> Staff Management** in Admin Web Portal.
  2. Tap **Add Staff Member**.
  3. Enter Staff Full Name, Department (Alteration, Finishing, Delivery), and Phone.
  4. Assign Role: `Staff`, `Manager`, `Accountant`, or `Delivery Staff`.
  5. Set temporary initial password.
  6. Instruct staff to update password upon initial login.
  7. When staff departs or resigns, immediately toggle **Deactivate Account**.
- **Expected Result**: Staff granted role-specific menu access; departed staff access instantly cut.
- **Exception Handling**: Staff forgetting passwords must request Owner reset via `POST /api/v1/auth/password-reset`.
- **Security Considerations**: Never create generic shared accounts; each tailor must have their own login.
- **Records Maintained**: `users` and `user_roles` tables.

---

### SOP-020: Data Backup and Recovery
- **SOP ID**: SOP-020
- **Title**: Data Backup and Recovery
- **Purpose**: Safeguard boutique financial records, customer fitting archives, and order history against hardware failure.
- **Scope**: Central server and cloud backup storage.
- **Responsible Person**: Senior DevOps Engineer / IT Administrator.
- **Prerequisites**: Automated cron backup script installed.
- **Step-by-Step Instructions**:
  1. System executes daily automated PostgreSQL backup at 02:00 AM IST via `scripts/backup_db.py`.
  2. Backup creates timestamped compressed archive (`aashima_backup_YYYYMMDD_HHMMSS.sql.gz`).
  3. Archive is copied to secondary off-site encrypted storage.
  4. Test restoration procedure monthly in isolated sandbox:
     ```bash
     py scripts/restore_db.py --file aashima_backup_latest.sql.gz
     ```
  5. Verify record counts for `customers`, `bookings`, `invoices`, and `measurements`.
- **Expected Result**: Recovery Point Objective (RPO) < 24 hours; Recovery Time Objective (RTO) < 15 minutes.
- **Exception Handling**: If backup fails, alert notification dispatched to administrator WhatsApp.
- **Security Considerations**: Backup archives are encrypted with AES-256 before transmission.
- **Records Maintained**: Backup execution logs in `/infrastructure/backups/`.
