# AASHIMA ERP – Known Limitations & Pending External Integrations

**Business Entity**: AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers (581 Turab Nagar)  
**System Status**: Not production ready; see `PROJECT_STATUS.md`

---

## 1. External Credential & Gateway Interfaces

### 1.1 SMS & WhatsApp Gateways
- **Interface Implemented**: Provider-independent `NotificationService` supporting Mock Driver, Twilio, Fast2SMS, and Gupshup.
- **Production Prerequisite**: Requires actual API tokens (`SMS_API_KEY`, `WHATSAPP_API_KEY`) and Indian DLT regulatory registration with TRAI for bulk SMS sender ID (`AASHMA`).
- **Current status**: Live SMS delivery requires provider credentials and was not verified. OTPs are no longer logged or included in returned WhatsApp links. Provider failure and rate-limit behavior still require production verification.

### 1.2 Physical Thermal Printer Hardware
- **Interface Implemented**: Native browser ESC/POS print driver with exact monospaced character bounds (32 chars for 58mm, 48 chars for 80mm) and high-contrast Base64 QR code rendering.
- **Hardware Requirement**: Physical verification requires pairing an actual Bluetooth or USB thermal receipt printer (e.g., Everycom, TVS, Epson ESC/POS). On non-connected devices, a pixel-perfect print preview drawer displays all claim details.

### 1.3 Optical Camera Barcode Scanning
- **Interface Implemented**: `html5-qrcode` integration with fallback numerical code input.
- **Browser Requirement**: Requires HTTPS context (or `localhost`) for browser permissions to access rear camera streams.

---

## 2. Recommended Phase 2 Enhancements
1. **Multi-Shop Clustering**: Expand from single-shop architecture to multi-unit inventory distribution if AASHIMA opens secondary ateliers in Delhi NCR.
2. **Fabric AI Defect Detection**: Integrate vision ML model to automatically classify zari pulls and silk stains during intake photo capture.
3. **Soundbox Bluetooth Integration**: Direct audio announcement of UPI payment collections at front desk counter.
