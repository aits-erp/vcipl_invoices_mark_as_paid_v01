import frappe
from frappe.utils import nowdate
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry


@frappe.whitelist()
def mark_invoice_paid(docname):
    if not docname:
        frappe.throw("Sales Invoice name is required")

    si = frappe.get_doc("Sales Invoice", docname)

    if si.docstatus == 2:
        frappe.throw("Invoice is Cancelled")

    if si.outstanding_amount <= 0:
        frappe.throw("Already Paid")

    # Submit if draft
    if si.docstatus == 0:
        si.submit()
        si.reload()

    # Create Payment Entry using ERPNext logic
    pe = get_payment_entry(
        dt="Sales Invoice",
        dn=si.name,
        party_amount=si.outstanding_amount
    )

    pe.posting_date = nowdate()

    # 🔥 IMPORTANT PART (force full allocation)
    for ref in pe.references:
        ref.allocated_amount = si.outstanding_amount

    pe.paid_amount = si.outstanding_amount
    pe.received_amount = si.outstanding_amount

    pe.insert(ignore_permissions=True)
    pe.submit()

    # 🔥 Reload invoice to update status
    si.reload()

    return {
        "status": "success",
        "invoice": si.name,
        "outstanding": si.outstanding_amount
    }