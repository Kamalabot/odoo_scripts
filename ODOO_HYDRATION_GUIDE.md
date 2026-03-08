# Odoo Excel Data Hydration Guide (Advanced)

To hydrate a true ERP database, you need to import data that has complex relational rules, like multi-line Purchase Orders or Invoices. 

We have built a custom, modular hydration tool in the `hydration/` directory that leverages Odoo's native `load()` API. This is the exact same API Odoo's web interface uses when you upload an Excel file, which means it fully supports External IDs and nested One2Many relationship lines.

## 1. Environment Setup (Windows)

The hydration scripts are designed to run in a Python Virtual Environment on your Windows host, pointing to the Odoo instance running in WSL (`localhost:8069`).

To install dependencies, just run the setup script once:
```cmd
cd hydration
setup_venv.bat
```

To use the tool moving forward:
```cmd
call venv\Scripts\activate.bat
python main.py --db ai_pf_db_clean --user admin --password admin --model purchase.order --file my_purchases.xlsx
```

## 2. Advanced Formats: The Power of External IDs

When importing ERP data, you cannot rely on text-matching names (what happens if two vendors are named "Acme Corp"?). You must use **External IDs**. 

An External ID is an arbitrary, unique string you assign to a row.

### Suffix Rules in Column Headers

1. **`id`**: This column contains the unique string *you* assign to create this record. 
    - E.g., `vendor_acme_corp`
2. **`/id`**: If a column ends in `/id` (e.g., `partner_id/id`), it expects an External ID of *another* record to link them together.
    - E.g., linking a Purchase Order to `vendor_acme_corp`.

---

## 3. Hydrating Purchase Orders (`purchase.order`)

A Purchase Order is a header (`purchase.order`) that has many lines (`purchase.order.line`). In Odoo, the relationship field from the order to the lines is called `order_line`.

To import an Order and its Lines at the same time, you use a single Excel file where the first row contains the Order header info, and subsequent rows belong to the same order. 

**Model to Target:** `purchase.order`

**Excel Example:**
| id | partner_id/id | date_order | order_line/product_id/id | order_line/product_qty | order_line/price_unit |
|---|---|---|---|---|---|
| PO_001 | vendor_acme | 2026-03-08 | prod_widget_a | 10 | 15.50 |
|        |             |            | prod_widget_b | 5  | 42.00 |
| PO_002 | vendor_beta | 2026-03-09 | prod_widget_c | 100 | 1.25 |

*Notice how row 2 leaves `id` and `partner_id/id` blank? Odoo's `load` API understands that this row is just another `order_line` belonging to `PO_001`.*

---

## 4. Hydrating Invoices (`account.move`)

An Invoice has the exact same header/line structure, but the model is different. 
- Header Model: `account.move`
- Lines Field: `invoice_line_ids` (which points to `account.move.line`)

**Model to Target:** `account.move`

**Excel Example:**
| id | move_type | partner_id/id | invoice_date | invoice_line_ids/product_id/id | invoice_line_ids/quantity | invoice_line_ids/price_unit |
|---|---|---|---|---|---|---|
| INV_001 | out_invoice | cust_alice | 2026-03-08 | prod_widget_a | 2 | 20.00 |
|         |             |            |            | prod_widget_b | 1 | 50.00 |
| INV_002 | in_invoice  | vendor_acme| 2026-03-08 | prod_widget_c | 50| 1.00  |

*(Note: `out_invoice` is a Customer Invoice, `in_invoice` is a Vendor Bill).*

---

## 5. Hydrating Contacts (`res.partner`)

Contacts can be nested! A company can have employees linked under it. 
- The relationship field from an employee to a company is `parent_id`.

**Model to Target:** `res.partner`

**Excel Example:**
| id | name | is_company | email | parent_id/id |
|---|---|---|---|---|
| comp_stark | Stark Industries | TRUE | info@stark.com | |
| emp_tony | Tony Stark | FALSE | tony@stark.com | comp_stark |
| emp_pepper | Pepper Potts | FALSE | pepper@stark.com | comp_stark |

---

## The Golden Rule for Hydration

If you do not know the technical names for fields on a model, **do not guess**.
1. Go into the Odoo Web UI.
2. Select an existing record.
3. Click **Action -> Export**.
4. Select "Import-Compatible Export".
5. Choose the fields you want.
6. The downloaded Excel file contains the exact column headers you must use for your own hydration files!
