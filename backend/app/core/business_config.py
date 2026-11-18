"""
AASHIMA ERP Business Configuration
Covers:
- Divisions: AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers
- Shop Details: 581, Turab Nagar, Ghaziabad, UP, India
- Services: Alteration, Deep Cleaning, Finishing, Ironing, Tailoring
- Standard Workflow Stages
- Tax rates (GST / Non-GST)
- Print formats: 58mm, 80mm, A4
"""

from decimal import Decimal
from enum import Enum
from typing import Dict, List, Any

class BusinessDivision(str, Enum):
    WOMENS_WORLD = "AASHIMA Women's World"
    STITCHERS_N_DRAPERS = "AASHIMA Stitchers 'N' Drapers"

class ServiceCategory(str, Enum):
    ALTERATION = "Alteration"
    DEEP_CLEANING = "Deep Cleaning / Dry Cleaning"
    FINISHING = "Finishing"
    IRONING = "Ironing"
    TAILORING = "Tailoring"

class WorkflowStage(str, Enum):
    BOOKING_RECEIVED = "Booking Received"
    ALTERATION = "Alteration"
    DEEP_CLEANING = "Deep Cleaning"
    FINISHING = "Finishing"
    DELIVERY_CENTRE = "Delivery Centre"
    READY_FOR_DELIVERY = "Ready for Delivery"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED = "Delivered"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"

class DepartmentCode(str, Enum):
    INTAKE = "INTAKE"
    ALTERATION = "ALTERATION"
    DEEP_CLEAN = "DEEP_CLEAN"
    FINISHING = "FINISHING"
    QC_PACKAGING = "QC_PACKAGING"
    DELIVERY_CENTRE = "DELIVERY_CENTRE"
    LOGISTICS = "LOGISTICS"

class UserRole(str, Enum):
    OWNER = "Owner"
    MANAGER = "Manager"
    STAFF = "Staff"
    ACCOUNTANT = "Accountant"
    DELIVERY_STAFF = "Delivery Staff"
    CUSTOMER = "Customer"

class PaymentMode(str, Enum):
    CASH = "Cash"
    UPI = "UPI"
    CARD = "Card"
    NET_BANKING = "NetBanking"
    SPLIT = "Split"

class PaymentStatus(str, Enum):
    UNPAID = "Unpaid"
    PARTIAL = "Partial"
    PAID = "Paid"
    REFUNDED = "Refunded"

class InvoiceType(str, Enum):
    GST = "GST"
    NON_GST = "Non-GST"

# Standard Services Seed Catalog
DEFAULT_SERVICES = [
    {
        "name": "Bespoke Bridal Lehenga Stitching",
        "category": ServiceCategory.TAILORING,
        "division": BusinessDivision.WOMENS_WORLD,
        "hsn_sac": "998822",
        "base_price": Decimal("2400.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 7,
        "requires_measurement": True,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Heavy Silk Saree Deep Dry Clean & Zari Polish",
        "category": ServiceCategory.DEEP_CLEANING,
        "division": BusinessDivision.WOMENS_WORLD,
        "hsn_sac": "999712",
        "base_price": Decimal("850.00"),
        "gst_rate": Decimal("18.00"),
        "turnaround_days": 3,
        "requires_measurement": False,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.DEEP_CLEANING,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Designer Blouse Stitching & Padding",
        "category": ServiceCategory.TAILORING,
        "division": BusinessDivision.WOMENS_WORLD,
        "hsn_sac": "998822",
        "base_price": Decimal("1100.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 4,
        "requires_measurement": True,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Kurta Pyjama Bespoke Tailoring",
        "category": ServiceCategory.TAILORING,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "998822",
        "base_price": Decimal("950.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 5,
        "requires_measurement": True,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Gentlemen Suit / Bandhgala Tailoring",
        "category": ServiceCategory.TAILORING,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "998822",
        "base_price": Decimal("3500.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 8,
        "requires_measurement": True,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Sherwani Deep Clean & Steam Form Press",
        "category": ServiceCategory.DEEP_CLEANING,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "999712",
        "base_price": Decimal("900.00"),
        "gst_rate": Decimal("18.00"),
        "turnaround_days": 3,
        "requires_measurement": False,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.DEEP_CLEANING,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Waistcoat / Trouser Alteration & Hemming",
        "category": ServiceCategory.ALTERATION,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "998822",
        "base_price": Decimal("250.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 2,
        "requires_measurement": False,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Bespoke Formal Shirt Tailoring",
        "category": ServiceCategory.TAILORING,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "998822",
        "base_price": Decimal("750.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 4,
        "requires_measurement": True,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Bespoke Formal Trouser / Pant Tailoring",
        "category": ServiceCategory.TAILORING,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "998822",
        "base_price": Decimal("900.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 4,
        "requires_measurement": True,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Nehru Jacket / Waistcoat Bespoke Tailoring",
        "category": ServiceCategory.TAILORING,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "998822",
        "base_price": Decimal("1800.00"),
        "gst_rate": Decimal("5.00"),
        "turnaround_days": 5,
        "requires_measurement": True,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.ALTERATION,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Men's 2-Piece / 3-Piece Suit Dry Clean & Steam Press",
        "category": ServiceCategory.DEEP_CLEANING,
        "division": BusinessDivision.STITCHERS_N_DRAPERS,
        "hsn_sac": "999712",
        "base_price": Decimal("650.00"),
        "gst_rate": Decimal("18.00"),
        "turnaround_days": 3,
        "requires_measurement": False,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.DEEP_CLEANING,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    },
    {
        "name": "Heirloom Pure Chiffon Saree Steam Finishing & Roll Press",
        "category": ServiceCategory.FINISHING,
        "division": BusinessDivision.WOMENS_WORLD,
        "hsn_sac": "999712",
        "base_price": Decimal("350.00"),
        "gst_rate": Decimal("18.00"),
        "turnaround_days": 2,
        "requires_measurement": False,
        "default_stages": [
            WorkflowStage.BOOKING_RECEIVED,
            WorkflowStage.FINISHING,
            WorkflowStage.DELIVERY_CENTRE,
            WorkflowStage.READY_FOR_DELIVERY
        ]
    }
]

# Standard Thermal and Slip Print Configs
PRINT_CONFIGS = {
    "58mm": {
        "chars_per_line": 32,
        "width_mm": 58,
        "dpi": 203,
        "title_font_size": 14,
        "body_font_size": 10,
        "qr_size_px": 160
    },
    "80mm": {
        "chars_per_line": 48,
        "width_mm": 80,
        "dpi": 203,
        "title_font_size": 16,
        "body_font_size": 11,
        "qr_size_px": 200
    },
    "A4": {
        "width_mm": 210,
        "height_mm": 297,
        "margin_mm": 15,
        "header_color": "#5B132B",
        "accent_color": "#C59B4B"
    }
}
