import pandas as pd
import os

def create_mocks():
    os.makedirs('samples', exist_ok=True)

    # 1. Contacts Model (res.partner)
    contacts = pd.DataFrame({
        'id': ['comp_acme', 'emp_alice', 'emp_bob', 'vendor_beta'],
        'name': ['Acme Corp', 'Alice Smith', 'Bob Jones', 'Beta Supplies'],
        'is_company': ['TRUE', 'FALSE', 'FALSE', 'TRUE'],
        'email': ['info@acme.com', 'alice@acme.com', 'bob@acme.com', 'sales@betasupplies.com'],
        'parent_id/id': ['', 'comp_acme', 'comp_acme', '']
    })
    contacts.to_excel('samples/1_contacts.xlsx', index=False)
    print("Created: samples/1_contacts.xlsx")

    # 2. Purchase Orders Model (purchase.order)
    # Notice the blank lines for the same ID to add multiple items to one order!
    pos = pd.DataFrame({
        'id': ['PO_001', '', 'PO_002'],
        'partner_id/id': ['comp_acme', '', 'vendor_beta'],
        'date_order': ['2026-03-08', '', '2026-03-09'],
        'order_line/name': ['Office Desk', 'Ergonomic Chair', '4K Monitor'],
        'order_line/product_qty': [10, 20, 5],
        'order_line/price_unit': [150.0, 75.0, 300.0]
    })
    pos.to_excel('samples/2_purchase_orders.xlsx', index=False)
    print("Created: samples/2_purchase_orders.xlsx")

    # 3. Invoices Model (account.move)
    invs = pd.DataFrame({
        'id': ['INV_001', '', 'INV_002'],
        'move_type': ['out_invoice', '', 'in_invoice'],  # out_invoice = Customer, in_invoice = Vendor Bill
        'partner_id/id': ['emp_alice', '', 'vendor_beta'],
        'invoice_date': ['2026-03-10', '', '2026-03-10'],
        'invoice_line_ids/name': ['Consulting Services', 'Software License', 'Cloud Hosting Fees'],
        'invoice_line_ids/quantity': [1, 2, 12],
        'invoice_line_ids/price_unit': [500.0, 250.0, 49.99]
    })
    invs.to_excel('samples/3_invoices.xlsx', index=False)
    print("Created: samples/3_invoices.xlsx")

    print("\nMock setup complete! All files ready for hydration testing.")

if __name__ == '__main__':
    create_mocks()
