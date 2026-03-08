import pandas as pd
import os

def create_mocks():
    os.makedirs('samples', exist_ok=True)

    # 1. Contacts Model (res.partner) (Updated with address details)
    contacts = pd.DataFrame({
        'id': ['comp_acme', 'emp_alice', 'emp_bob', 'vendor_beta'],
        'name': ['Acme Corp', 'Alice Smith', 'Bob Jones', 'Beta Supplies'],
        'is_company': ['TRUE', 'FALSE', 'FALSE', 'TRUE'],
        'email': ['info@acme.com', 'alice@acme.com', 'bob@acme.com', 'sales@betasupplies.com'],
        'street': ['123 Industrial Way', '', '', '456 Supplier Blvd'],
        'city': ['Metropolis', '', '', 'Gotham'],
        'zip': ['10001', '', '', '10002'],
        'parent_id/id': ['', 'comp_acme', 'comp_acme', '']
    })
    contacts.to_excel('samples/1_contacts.xlsx', index=False)
    print("Created: samples/1_contacts.xlsx")

    # 2. Purchase Orders Model (purchase.order)
    # Notice the blank lines for the same ID to add multiple items to one order!
    pos = pd.DataFrame({
        'id': ['PO_001', 'PO_001', 'PO_002'], # ID must repeat for lines to group correctly!
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
        'id': ['INV_001', 'INV_001', 'INV_002'], # ID must repeat for lines to group correctly!
        'move_type': ['out_invoice', 'out_invoice', 'in_invoice'],  # out_invoice = Customer, in_invoice = Vendor Bill
        'partner_id/id': ['emp_alice', 'emp_alice', 'vendor_beta'], # Must repeat for grouped lines
        'invoice_date': ['2026-03-10', '2026-03-10', '2026-03-10'],
        'invoice_line_ids/name': ['Consulting Services', 'Software License', 'Cloud Hosting Fees'],
        'invoice_line_ids/quantity': [1, 2, 12],
        'invoice_line_ids/price_unit': [500.0, 250.0, 49.99]
    })
    invs.to_excel('samples/3_invoices.xlsx', index=False)
    print("Created: samples/3_invoices.xlsx")

    print("Created: samples/3_invoices.xlsx")

    # 4. Products & Inventory (product.template)
    products = pd.DataFrame({
        'id': ['prod_widget_a', 'prod_widget_b', 'prod_widget_c'],
        'name': ['Office Desk', 'Ergonomic Chair', '4K Monitor'],
        'type': ['consu', 'consu', 'consu'], # In later Odoo versions, 'product' was renamed to 'consu' (consumable) or 'service'. Let's use 'consu' to be safe.
        'list_price': [199.99, 149.99, 399.99],
        'standard_price': [80.00, 60.00, 200.00], # Cost
        'barcode': ['1234567890123', '1234567890124', '1234567890125']
    })
    products.to_excel('samples/4_products.xlsx', index=False)
    print("Created: samples/4_products.xlsx")

    # 5. Employees & HR (hr.employee)
    # Using simple text fields like 'department_id' (which maps to name by default in Odoo load)
    # Note: Odoo standard `load` will reject ManyToMany/Many2One if the record doesn't exist.
    # For a fresh DB, linking to non-existent Departments/Jobs via `/name` throws "Cannot create Many-To-One records indirectly".
    # Therefore we will just leave them blank or use fields that do not force relationship creation on empty DBs.
    employees = pd.DataFrame({
        'id': ['hr_emp_alice', 'hr_emp_bob'],
        'name': ['Alice Smith', 'Bob Jones'],
        'work_email': ['alice@ourcompany.com', 'bob@ourcompany.com'],
        'job_title': ['Sales Director', 'Senior Developer'] # job_title is a Char field, job_id is Many2One.
    })
    employees.to_excel('samples/5_employees.xlsx', index=False)
    print("Created: samples/5_employees.xlsx")

    # 6. Sales Orders / Quotations (sale.order)
    sales = pd.DataFrame({
        'id': ['SO_001', 'SO_001', 'SO_002'], # ID must repeat for lines to group correctly!
        'partner_id/id': ['comp_acme', 'comp_acme', 'emp_bob'], # Selling to these contacts. Must repeat for lines under the same document.
        'date_order': ['2026-03-12', '2026-03-12', '2026-03-13'],
        # IMPORTANT: Product templates are product.template. Odoo sales lines link strictly to product.product (variants).
        # We can bypass the `product.product` external ID error by letting Odoo map it through the template ID column.
        'order_line/product_template_id/id': ['prod_widget_a', 'prod_widget_b', 'prod_widget_c'],
        'order_line/name': ['Office Desk', 'Ergonomic Chair', '4K Monitor'], # Required by Odoo for SO lines!
        'order_line/product_uom_qty': [5, 5, 2],
        'order_line/price_unit': [200.00, 150.00, 400.00]
    })
    sales.to_excel('samples/6_sales_orders.xlsx', index=False)
    print("Created: samples/6_sales_orders.xlsx")

    # 7. CRM Leads / Opportunities (crm.lead)
    crm = pd.DataFrame({
        'id': ['crm_opp_1', 'crm_opp_2'],
        'name': ['Need 50 Office Desks for New HQ', 'Interested in 4K Monitors'],
        'expected_revenue': [10000.00, 4000.00],
        'probability': [80, 20],
        'partner_id/id': ['comp_acme', 'vendor_beta'], # Linking lead to a contact
        'type': ['opportunity', 'lead']
    })
    crm.to_excel('samples/7_crm_leads.xlsx', index=False)
    print("Created: samples/7_crm_leads.xlsx")

    # 8. Manufacturing Orders (mrp.production)
    mrp = pd.DataFrame({
        'id': ['MO_001', 'MO_002'],
        # MRP Production strictly builds product.product (variants), not product.template.
        # Since Odoo does not auto-generate External IDs for variants when templates are imported,
        # we MUST map to the variant by its Display Name instead of an External ID path!
        'product_id': ['Office Desk', 'Ergonomic Chair'], 
        'product_qty': [10, 50],
        'date_start': ['2026-03-15', '2026-03-16'] # Changed from invalid 'date_format' to 'date_start'
    })
    mrp.to_excel('samples/8_manufacturing.xlsx', index=False)
    print("Created: samples/8_manufacturing.xlsx")

    print("\nMock setup complete! All files ready for hydration testing.")

if __name__ == '__main__':
    create_mocks()
