#!/usr/bin/env python3
"""
AASHIMA ERP - Master Ecosystem Runner
Initializes database seed, verifies models, and serves all applications on port 8000:
- Customer Web: http://localhost:8000/
- Admin Dashboard: http://localhost:8000/admin/
- Android POS: http://localhost:8000/mobile/
- Interactive Swagger: http://localhost:8000/api/docs
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.services.seed_data import run_seed
import uvicorn

def main():
    print("=" * 70)
    print("  AASHIMA ERP - COMPLETE BUSINESS MANAGEMENT ECOSYSTEM")
    print("  581, Turab Nagar, Ghaziabad, Uttar Pradesh, India")
    print("=" * 70)

    # 1. Verify database schema & foundational atelier settings (preserve real customer/order data)
    print("\n[1/2] Verifying database schema & foundational atelier data...")
    run_seed(clean_synthetic=False)

    # 2. Launch FastAPI with all frontends mounted
    print("\n[2/2] Launching Central Server with all 3 Applications on Port 8000...")
    print("\n" + "-" * 70)
    print("  Customer Live Tracking Portal : http://localhost:8000/")
    print("  Enterprise Admin Dashboard    : http://localhost:8000/admin/")
    print("  Android Mobile POS App        : http://localhost:8000/mobile/")
    print("  Interactive Swagger API Docs  : http://localhost:8000/api/docs")
    print("  System Health Endpoint        : http://localhost:8000/health")
    print("-" * 70 + "\n")

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")

if __name__ == "__main__":
    main()
