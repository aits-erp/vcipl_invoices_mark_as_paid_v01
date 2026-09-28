import frappe
from frappe.utils import getdate, add_months, today


def validate_posting_date(doc, method=None):

    # Only DocTypes having posting_date field
    if not doc.meta.has_field("posting_date"):
        return

    # Skip if empty
    if not doc.posting_date:
        return

    posting_date = getdate(doc.posting_date)

    # One month back from today
    cutoff_date = add_months(getdate(today()), -1)

    if posting_date < cutoff_date:
        frappe.throw(
            f"Posting Date cannot be earlier than "
            f"{cutoff_date.strftime('%d-%m-%Y')}. "
            f"Only previous one month is allowed."
        )