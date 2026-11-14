import frappe
from frappe.utils import getdate, add_months, today


DATE_FIELDS = [
    "posting_date",
    "transaction_date",
    "schedule_date",
    "due_date",
]

CANCELLATION_OVERRIDE_ROLE = "Sales Invoice Cancellation Override"


def enable_cancellation_override(doc, method=None):
    if frappe.has_role(CANCELLATION_OVERRIDE_ROLE):
        frappe.flags.sales_invoice_paid_button_cancellation_override = (
            frappe.flags.sales_invoice_paid_button_cancellation_override or 0
        ) + 1


def disable_cancellation_override(doc, method=None):
    if frappe.flags.sales_invoice_paid_button_cancellation_override:
        frappe.flags.sales_invoice_paid_button_cancellation_override -= 1

def validate_posting_date(doc, method=None):

    if frappe.flags.sales_invoice_paid_button_cancellation_override:
        return

    cutoff_date = add_months(getdate(today()), -1)

    for fieldname in DATE_FIELDS:

        if not doc.meta.has_field(fieldname):
            continue

        date_value = doc.get(fieldname)

        if not date_value:
            continue

        if getdate(date_value) < cutoff_date:
            frappe.throw(
                f"{doc.meta.get_label(fieldname)} cannot be earlier than "
                f"{cutoff_date.strftime('%d-%m-%Y')}. "
                f"Only previous one month is allowed."
            )
