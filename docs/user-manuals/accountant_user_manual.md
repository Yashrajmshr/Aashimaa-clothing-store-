# AASHIMA ERP – Chief Accountant User Manual

**Target Audience**: Head of Finance, Cashier, and Billing Clerks  
**Platform**: AASHIMA Admin Web Portal / Financial Terminal  

---

## 1. Financial Architecture & Precision Standards
- All calculations utilize fixed-point `Decimal` (`NUMERIC(12, 2)`) math.
- Never manually calculate tax or round-off; the backend validates every invoice line item.
- Strict segregation of GST (5% for tailoring, 18% for dry cleaning) vs Non-GST counter slips.

---

## 2. Managing the Counter Daybook
1. Open **Financials -> Daybook Ledger** on the Admin Web Portal.
2. Review real-time splits:
   - Cash Collected
   - UPI Collections (Verified against soundbox / bank statement)
   - Card Swipes
3. Total slips billed count and average ticket size.
4. Execute daily closing reconciliation at 9:00 PM IST (SOP-018).

---

## 3. GST Tax Invoice Generation
1. Select any completed booking from the invoice queue.
2. Tap **Create Invoice**, selecting `GST Tax Invoice`.
3. System compiles itemized HSN/SAC codes, CGST, and SGST amounts.
4. Tap **Download Tax PDF** to obtain the official A4 signed invoice for client tax filing.

---

## 4. Expense Auditing & Karigar Advances
1. Navigate to **Expenses & P&L**.
2. Click **Record Expense Voucher** to log shop expenses (threads, zips, packaging bags, utility, karigar advance).
3. System updates net monthly profit estimates.
