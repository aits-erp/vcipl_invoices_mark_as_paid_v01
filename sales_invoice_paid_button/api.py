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
    pe.reference_no = si.name
    pe.reference_date = nowdate()

    # optional fallback
    if not pe.mode_of_payment:
        default_mop = frappe.db.get_value(
            "Mode of Payment Account",
            {"company": si.company},
            "parent"
        )
        if default_mop:
            pe.mode_of_payment = default_mop

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
        "payment_entry": pe.name
    }
