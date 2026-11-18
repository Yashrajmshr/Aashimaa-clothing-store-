import os
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.app.core.config import settings
from backend.app.models.booking import Booking
from backend.app.models.customer import Customer
from backend.app.models.billing import Invoice, InvoiceItem, Payment, PaymentReceipt, GSTConfiguration

def round_currency(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def generate_invoice_number(db: Session) -> str:
    year = datetime.utcnow().year
    count = db.query(Invoice).count() + 1
    return f"ASH-INV-{year}-{count:04d}"

def generate_payment_reference(db: Session) -> str:
    year = datetime.utcnow().year
    count = db.query(Payment).count() + 1
    return f"PAY-{year}-{count:04d}"

def generate_receipt_number(db: Session) -> str:
    year = datetime.utcnow().year
    count = db.query(PaymentReceipt).count() + 1
    return f"REC-{year}-{count:04d}"

def create_invoice_for_booking(
    db: Session,
    booking_id: int,
    invoice_type: str = "GST",
    discount_amount: Decimal = Decimal("0.00"),
    extra_charges: Decimal = Decimal("0.00"),
    user_id: Optional[int] = None
) -> Invoice:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    existing_invoice = db.query(Invoice).filter(Invoice.booking_id == booking_id).first()
    if existing_invoice:
        return existing_invoice

    customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()
    invoice_num = generate_invoice_number(db)

    subtotal = Decimal("0.00")
    total_cgst = Decimal("0.00")
    total_sgst = Decimal("0.00")
    items_to_create = []

    for garment in booking.garments:
        for srv in garment.services:
            qty = garment.quantity
            unit_price = srv.price
            taxable_val = round_currency(unit_price * qty)
            subtotal += taxable_val

            if invoice_type == "GST":
                rate = srv.gst_rate
                half_rate = rate / Decimal("2.0")
                cgst = round_currency(taxable_val * (half_rate / Decimal("100.0")))
                sgst = round_currency(taxable_val * (half_rate / Decimal("100.0")))
                item_total = taxable_val + cgst + sgst
                total_cgst += cgst
                total_sgst += sgst
            else:
                cgst = Decimal("0.00")
                sgst = Decimal("0.00")
                rate = Decimal("0.00")
                item_total = taxable_val

            items_to_create.append({
                "garment_id": garment.id,
                "item_description": f"{garment.garment_name} - {srv.service_name}",
                "hsn_sac": srv.service.hsn_sac if srv.service else "998822",
                "quantity": qty,
                "unit_price": unit_price,
                "item_discount": Decimal("0.00"),
                "taxable_value": taxable_val,
                "gst_rate": rate,
                "cgst_amount": cgst,
                "sgst_amount": sgst,
                "total_item_amount": item_total
            })

    total_tax = total_cgst + total_sgst
    grand_total = round_currency(subtotal - discount_amount + extra_charges + total_tax)
    paid = booking.advance_paid
    balance = round_currency(grand_total - paid)

    invoice = Invoice(
        invoice_number=invoice_num,
        booking_id=booking.id,
        customer_id=booking.customer_id,
        invoice_type=invoice_type,
        division=booking.division,
        invoice_date=datetime.utcnow(),
        subtotal_amount=subtotal,
        discount_amount=discount_amount,
        extra_charges=extra_charges,
        taxable_amount=subtotal,
        cgst_amount=total_cgst,
        sgst_amount=total_sgst,
        igst_amount=Decimal("0.00"),
        total_tax_amount=total_tax,
        grand_total=grand_total,
        round_off=Decimal("0.00"),
        paid_amount=paid,
        outstanding_balance=balance,
        generated_by_user_id=user_id
    )
    db.add(invoice)
    db.flush()

    for item_data in items_to_create:
        inv_item = InvoiceItem(
            invoice_id=invoice.id,
            **item_data
        )
        db.add(inv_item)

    # Generate PDF Invoice on disk
    pdf_filename = f"{invoice.invoice_number}.pdf"
    pdf_filepath = os.path.join(settings.INVOICE_DIR, pdf_filename)
    generate_invoice_pdf(invoice, customer, booking, pdf_filepath)
    invoice.pdf_path = f"/media/invoices/{pdf_filename}"

    db.commit()
    db.refresh(invoice)
    return invoice

def record_payment(
    db: Session,
    booking_id: int,
    amount: Decimal,
    payment_type: str = "Partial",
    payment_mode: str = "UPI",
    transaction_id: Optional[str] = None,
    notes: Optional[str] = None,
    user_id: Optional[int] = None
) -> Tuple[Payment, PaymentReceipt]:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    customer = db.query(Customer).filter(Customer.id == booking.customer_id).first()

    pay_ref = generate_payment_reference(db)
    rec_num = generate_receipt_number(db)

    # Add to advance/paid
    booking.advance_paid = round_currency(booking.advance_paid + amount)
    booking.balance_due = round_currency(booking.net_amount - booking.advance_paid)

    if booking.balance_due <= Decimal("0.00"):
        booking.payment_status = "Paid"
        booking.balance_due = Decimal("0.00")
    else:
        booking.payment_status = "Partial"

    # Update customer lifetime stats
    if customer:
        customer.outstanding_dues = max(Decimal("0.00"), round_currency(customer.outstanding_dues - amount))

    # Create Payment record
    payment = Payment(
        payment_reference=pay_ref,
        booking_id=booking.id,
        customer_id=booking.customer_id,
        amount=amount,
        payment_type=payment_type,
        payment_mode=payment_mode,
        transaction_id=transaction_id,
        notes=notes,
        collected_by_user_id=user_id
    )
    db.add(payment)
    db.flush()

    # Create Receipt record
    receipt = PaymentReceipt(
        receipt_number=rec_num,
        payment_id=payment.id,
        amount_paid=amount,
        remaining_balance=booking.balance_due
    )
    db.add(receipt)

    # If invoice exists, update paid amount & balance
    invoice = db.query(Invoice).filter(Invoice.booking_id == booking_id).first()
    if invoice:
        invoice.paid_amount = booking.advance_paid
        invoice.outstanding_balance = booking.balance_due
        receipt.invoice_id = invoice.id

    db.commit()
    db.refresh(payment)
    db.refresh(receipt)
    return payment, receipt

def generate_invoice_pdf(invoice: Invoice, customer: Customer, booking: Booking, file_path: str):
    """
    Generate professional A4 PDF invoice matching AASHIMA Regal Atelier visual style.
    """
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    burgundy = colors.HexColor("#5B132B")
    gold = colors.HexColor("#C59B4B")
    charcoal = colors.HexColor("#201A1C")
    light_rose = colors.HexColor("#FAF7F5")

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=burgundy,
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "InvoiceSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=charcoal,
        leading=13
    )

    story.append(Paragraph("AASHIMA ATELIER & DRY-CLEAN ERP", title_style))
    story.append(Paragraph("AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers", sub_style))
    story.append(Paragraph("581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India | Phone: +91 98102 44321", sub_style))
    story.append(Paragraph(f"GSTIN: {settings.SHOP_GSTIN} | Division: {invoice.division}", sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=burgundy, spaceAfter=12))

    # Meta Table: Customer & Invoice Details
    cust_addr = customer.addresses[0].address_line1 if customer.addresses else "Ghaziabad, UP"
    meta_data = [
        [
            Paragraph(f"<b>BILLED TO:</b><br/>{customer.full_name} ({customer.patron_tier})<br/>Phone: {customer.phone}<br/>Address: {cust_addr}<br/>Unit: {customer.unit_reference or 'N/A'}", sub_style),
            Paragraph(f"<b>INVOICE NO:</b> {invoice.invoice_number}<br/><b>BOOKING REF:</b> #{booking.booking_number}<br/><b>DATE:</b> {invoice.invoice_date.strftime('%d-%b-%Y')}<br/><b>TYPE:</b> {invoice.invoice_type} TAX INVOICE", sub_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 250])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Items Table
    headers = ["#", "Garment & Service Description", "HSN/SAC", "Qty", "Rate (₹)", "Taxable (₹)", "GST", "Total (₹)"]
    table_data = [headers]

    for idx, item in enumerate(invoice.items, 1):
        table_data.append([
            str(idx),
            item.item_description,
            item.hsn_sac,
            str(item.quantity),
            f"{item.unit_price:.2f}",
            f"{item.taxable_value:.2f}",
            f"{item.gst_rate:.1f}%",
            f"{item.total_item_amount:.2f}"
        ])

    table_data.append(["", "", "", "", "", "Subtotal:", "", f"₹ {invoice.subtotal_amount:.2f}"])
    if invoice.invoice_type == "GST":
        table_data.append(["", "", "", "", "", "CGST:", "", f"₹ {invoice.cgst_amount:.2f}"])
        table_data.append(["", "", "", "", "", "SGST:", "", f"₹ {invoice.sgst_amount:.2f}"])
    table_data.append(["", "", "", "", "", "Grand Total:", "", f"₹ {invoice.grand_total:.2f}"])
    table_data.append(["", "", "", "", "", "Advance Paid:", "", f"₹ {invoice.paid_amount:.2f}"])
    table_data.append(["", "", "", "", "", "Balance Due:", "", f"₹ {invoice.outstanding_balance:.2f}"])

    items_table = Table(table_data, colWidths=[25, 195, 55, 30, 55, 65, 40, 60])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), burgundy),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1, len(invoice.items)), 0.5, colors.lightgrey),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('FONTNAME', (5, len(invoice.items)+1), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20))

    # Terms & Signature
    story.append(Paragraph("<b>Terms & Conditions:</b><br/>1. Goods once delivered cannot be claimed for unverified damages.<br/>2. Please collect garments within 30 days of the ready date.<br/>3. Subject to Ghaziabad jurisdiction.", sub_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Authorised Signatory<br/><b>For AASHIMA</b>", sub_style))

    doc.build(story)
