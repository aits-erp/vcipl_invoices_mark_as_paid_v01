import frappe
from frappe.utils import nowdate
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry


@frappe.whitelist()
def mark_invoice_paid(docname):
    if not docname:
        frappe.throw("Sales Invoice name is required")

    si = frappe.get_doc("Sales Invoice", docname)

    if si.docstatus == 2:
        frappe.throw("Sales Invoice is Cancelled")

    if si.outstanding_amount <= 0:
        frappe.throw("Sales Invoice is already fully Paid")

    # If invoice is draft, submit first
    if si.docstatus == 0:
        si.submit()
        si.reload()

    outstanding_amount = si.outstanding_amount

    pe = get_payment_entry(
        dt="Sales Invoice",
        dn=si.name,
        party_amount=outstanding_amount
    )

    pe.posting_date = nowdate()

    # mandatory for bank transaction
    pe.reference_no = si.name
    pe.reference_date = nowdate()

    # force full allocation
    pe.paid_amount = outstanding_amount
    pe.received_amount = outstanding_amount

    for ref in pe.references:
        if ref.reference_doctype == "Sales Invoice" and ref.reference_name == si.name:
            ref.allocated_amount = outstanding_amount

    pe.insert(ignore_permissions=True)
    pe.submit()

    frappe.db.commit()

    si.reload()

    return {
        "status": "success",
        "invoice": si.name,
        "payment_entry": pe.name,
        "outstanding_amount": si.outstanding_amount
    }
