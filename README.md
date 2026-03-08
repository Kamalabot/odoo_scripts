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

**Crucial Logic for Multi-Line Documents:** To group multiple items under one parent document, you **must repeat the header context** on every line. This includes the parent `id`, the related `partner_id/id`, and structural fields like `date_order`. If you omit them, Odoo's engine will throw a "Missing required value for field X" error because it loses track of the parent context.

**Model to Target:** `purchase.order`

**Excel Example:**
| id | partner_id/id | date_order | order_line/name | order_line/product_qty | order_line/price_unit |
|---|---|---|---|---|---|
| PO_001 | vendor_acme | 2026-03-08 | Office Desk | 10 | 15.50 |
| PO_001 | vendor_acme | 2026-03-08 | Ergonomic Chair | 5  | 42.00 |
| PO_002 | vendor_beta | 2026-03-09 | 4K Monitor | 100 | 1.25 |

---

## 4. Hydrating Invoices (`account.move`)

An Invoice has the exact same header/line structure, but the model is different. 
- Header Model: `account.move`
- Lines Field: `invoice_line_ids` (which points to `account.move.line`)

**Model to Target:** `account.move`

**Excel Example:**
| id | move_type | partner_id/id | invoice_date | invoice_line_ids/name | invoice_line_ids/quantity | invoice_line_ids/price_unit |
|---|---|---|---|---|---|---|
| INV_001 | out_invoice | cust_alice | 2026-03-08 | Consulting | 2 | 20.00 |
| INV_001 | out_invoice | cust_alice | 2026-03-08 | License    | 1 | 50.00 |
| INV_002 | in_invoice  | vendor_acme| 2026-03-10 | Hosting    | 50| 1.00  |

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

## 6. Hydrating Products & Inventory (`product.template`)

Products are typically created at the template level which automatically generates the variant (`product.product`).

**Important Note:** In newer Odoo versions, the `type` field value `product` was deprecated. Ensure you use `consu` (Consumable) or `service`.

**Model to Target:** `product.template`

**Excel Example:**
| id | name | type | list_price | standard_price | barcode |
|---|---|---|---|---|---|
| prod_desk | Office Desk | consu | 199.99 | 80.00 | 123456789 |
| prod_chair | Ergonomic Chair | consu | 149.99 | 60.00 | 987654321 |

---

## 7. Hydrating Employees & HR (`hr.employee`)

**Common Error:** `Cannot create Many-To-One records indirectly`.
If you map to textual relations like `department_id/name` on an *empty* database, Odoo throws this exception. To prevent this during mock data scaffolding, map to simple text fields (like `job_title` instead of `job_id/name`) or ensure the parent lookup exists prior.

**Model to Target:** `hr.employee`

**Excel Example:**
| id | name | work_email | job_title |
|---|---|---|---|
| hr_alice | Alice Smith | alice@ourcompany.com | Sales Director |
| hr_bob | Bob Jones | bob@ourcompany.com | Senior Developer |

---

## 8. Hydrating Sales Orders & Quotations (`sale.order`)

Sales orders are structured exactly like Purchase Orders. A header `sale.order` with an `order_line` relationship pointing to `sale.order.line`.

**Bug Resolved:** `Invalid external ID: expected model 'product.product', found 'product.template'`
When hydrating SO lines, Odoo demands the `product.product` variant natively. But our imported templates are `product.template`.
- **RCA/Logic**: Odoo automatically converts templates to variants upon creation. Thus, instead of providing `order_line/product_id/id` (which strictly expects a variant External ID), we provide `order_line/product_template_id/id`. This directs Odoo to lookup the parent template, and implicitly fetch the hidden variant under it! We also found that `order_line/name` is fiercely required for Sales lines.

**Model to Target:** `sale.order`

**Excel Example:**
| id | partner_id/id | date_order | order_line/product_template_id/id | order_line/name | order_line/product_uom_qty | order_line/price_unit |
|---|---|---|---|---|---|---|
| SO_001 | cust_alice | 2026-03-12 | prod_desk | Office Desk | 5 | 200.00 |
| SO_001 | cust_alice | 2026-03-12 | prod_chair | Ergonomic Chair | 5 | 150.00 |

---

## 9. Hydrating CRM Leads & Opportunities (`crm.lead`)

CRM data uses a single model for both raw Leads and qualified Opportunities, driven by the `type` field.

**Model to Target:** `crm.lead`

**Excel Example:**
| id | name | expected_revenue | probability | partner_id/id | type |
|---|---|---|---|---|---|
| crm_1 | Need 50 Desks | 10000.00 | 80 | cust_alice | opportunity |
| crm_2 | Interested in App | 0.00 | 10 | | lead |

---

## 10. Hydrating Manufacturing Orders (`mrp.production`)

A Manufacturing order dictates what product to build, how many, and by when. 

**Bug Resolved:** `Invalid field name 'date_format'` and `Missing required value for the field 'Product' (product_id)`
- **`date_format`**: The internal field is actually `date_start`. 
- **MRP Variant Resolution**: We wrote `check_product_variants.py` to query `ir.model.data` via XML-RPC. We proved that Odoo does *not* auto-assign an External ID (`__import__.product_...`) to auto-created `product.product` variants! Therefore, mapping via `product_id/id` OR `product_id/product_tmpl_id/id` fails miserably.
- **RCA/Logic Fix**: The only reliable way to map variants to MRP lines on an empty database is to abandon the `/id` suffix completely and do a literal Display Name match (`product_id`).

**Model to Target:** `mrp.production`

**Excel Example:**
| id | product_id | product_qty | date_start |
|---|---|---|---|
| MO_001 | Office Desk | 10 | 2026-03-15 |

---

## The Golden Rule for Hydration

If you do not know the technical names for fields on a model, **do not guess**.
1. Go into the Odoo Web UI.
2. Select an existing record.
3. Click **Action -> Export**.
4. Select "Import-Compatible Export".
5. Choose the fields you want.
6. The downloaded Excel file contains the exact column headers you must use for your own hydration files!
