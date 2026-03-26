frappe.listview_settings['Sales Invoice'] = {
    onload(listview) {
        listview.page.add_action_item(__('Mark as Paid'), async function () {
            const selected = listview.get_checked_items();

            if (!selected || !selected.length) {
                frappe.msgprint(__('Please select at least one Sales Invoice.'));
                return;
            }

            frappe.confirm(
                __('Are you sure you want to mark the selected invoice(s) as Paid?'),
                async function () {
                    frappe.dom.freeze(__('Processing...'));

                    try {
                        for (const row of selected) {
                            await frappe.call({
                                method: 'sales_invoice_paid_button.api.mark_invoice_paid',
                                args: {
                                    docname: row.name
                                }
                            });
                        }

                        frappe.msgprint(__('Selected invoice(s) marked as Paid successfully.'));
                        listview.refresh();
                    } catch (e) {
                        console.error(e);
                        frappe.msgprint(__('Error while marking invoice(s) as Paid.'));
                    } finally {
                        frappe.dom.unfreeze();
                    }
                }
            );
        });
    }
};