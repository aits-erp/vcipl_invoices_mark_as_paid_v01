import frappe
from frappe.utils import getdate, add_months, today


DATE_FIELDS = [
    "posting_date",
    "transaction_date",
    "schedule_date",
    "due_date",
]

CANCELLATION_OVERRIDE_ROLE = "Sales Invoice Cancellation Override"
    

def validate_posting_date(doc, method=None):

    if doc.docstatus == 2 and frappe.has_role(CANCELLATION_OVERRIDE_ROLE):
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
