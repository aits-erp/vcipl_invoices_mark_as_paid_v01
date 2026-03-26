import frappe
from frappe.utils import nowdate


@frappe.whitelist()
def mark_invoice_paid(docname):
    if not docname:
        frappe.throw("Sales Invoice name is required")

    doc = frappe.get_doc("Sales Invoice", docname)

    if doc.docstatus == 2:
        frappe.throw(f"Sales Invoice {docname} is cancelled")

    if doc.outstanding_amount <= 0:
        frappe.throw(f"Sales Invoice {docname} is already fully paid")

    if doc.docstatus == 0:
        doc.submit()
        doc.reload()

    outstanding_amount = doc.outstanding_amount

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = doc.customer
    pe.company = doc.company
    pe.posting_date = nowdate()
    pe.paid_amount = outstanding_amount
    pe.received_amount = outstanding_amount
    pe.reference_no = doc.name
    pe.reference_date = nowdate()

    pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": doc.name,
        "allocated_amount": outstanding_amount
    })

    pe.insert(ignore_permissions=True)
    pe.submit()

    frappe.db.commit()

    return {"status": "success", "invoice": doc.name}