# 💡 Two New Odoo Addon Ideas

Each addon is a **completely standalone module** — no dependency on `estate`.  
Each one teaches a **distinct set of Odoo concepts** not covered by the estate addon.

---

## Odoo Concepts Already Covered in `estate`

*(These won't be the focus in the new addons below)*

| Concept | Where in estate |
|---|---|
| `models.Model`, basic fields | `estate_property.py` |
| `Many2one`, `One2many`, `Many2many` | type/tag/offer relations |
| Tree, Form, Search views | all views |
| `@api.depends` computed fields | `total_area`, `best_price` |
| `@api.constrains` | selling price validation |
| `create()` ORM override | offer creation hook |
| Button actions (`type="object"`) | Sell/Cancel/Accept/Refuse |
| `ir.model.access.csv` security | security file |
| Status bar widget | property state |

---

---

# 📚 Addon Idea 1: Library Management System (`library`)

## What It Does

A public library management system where librarians manage books, members borrow books, and the system tracks loan history, due dates, and overdue items. Automated reminders run on a schedule.

## New Odoo Concepts You'll Learn

| Concept | What It Is |
|---|---|
| **`TransientModel` (Wizard)** | Temporary form pop-up for multi-step operations — data deleted after session |
| **Kanban View** | Card-based board view, grouped by state |
| **`@api.onchange`** | Reacts to field changes in the UI *before* saving (no DB write) |
| **Sequence (`ir.sequence`)** | Auto-incremented formatted IDs (e.g. LIB/2024/00042) |
| **Scheduled Action (Cron)** | Python method that Odoo runs automatically on a schedule |
| **QWeb Report** | PDF/HTML report generated from a Jinja-like template (`ir.actions.report`) |
| **`_sql_constraints`** | Database-level UNIQUE constraints (not just Python validation) |
| **`digits` on Float** | Control decimal precision on numeric fields |

---

## 📊 DB Layer — All Tables

### `library.book` → table `library_book`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR NOT NULL | Book title |
| `isbn` | VARCHAR | **UNIQUE** constraint at DB level (`_sql_constraints`) |
| `author_ids` | *(junction table)* | Many2many → `res.partner` (reuse existing contacts as authors) |
| `category_ids` | *(junction table)* | Many2many → `library.book.category` |
| `total_copies` | INTEGER | How many physical copies the library owns |
| `available_copies` | *(no col)* | Computed: `total_copies - active_loans` |
| `state` | VARCHAR | `available` / `unavailable` / `archived` |
| `cover_image` | BYTEA | `fields.Binary` — stores file bytes in DB |
| `description` | TEXT | — |
| `published_date` | DATE | — |
| `ref` | VARCHAR | Auto-generated from `ir.sequence` e.g. `LIB/0001` |

**SQL constraint example:**
```python
_sql_constraints = [
    ('isbn_unique', 'UNIQUE(isbn)', 'ISBN must be unique across all books.'),
]
```
→ Odoo runs `ALTER TABLE library_book ADD CONSTRAINT isbn_unique UNIQUE (isbn)` on install.  
This is enforced at the **PostgreSQL level** — even direct DB inserts are blocked.

---

### `library.member` → table `library_member`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `partner_id` | INTEGER FK → res_partner | Many2one — reuses Odoo contact (name, email, phone) |
| `member_ref` | VARCHAR | From `ir.sequence`: `MEM/2024/00001` |
| `membership_date` | DATE | When they joined |
| `expiry_date` | DATE | When their membership expires |
| `state` | VARCHAR | `active` / `expired` / `suspended` |
| `loan_ids` | *(no col)* | One2many reverse → library.loan |
| `active_loan_count` | *(no col)* | Computed integer |
| `max_books` | INTEGER | Default 3 — max simultaneous loans |

**`ir.sequence` pattern:**
```python
# In create() override:
member.member_ref = self.env['ir.sequence'].next_by_code('library.member')
```
Odoo manages an auto-increment counter per sequence code.

---

### `library.loan` → table `library_loan`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `book_id` | INTEGER FK → library_book | Many2one |
| `member_id` | INTEGER FK → library_member | Many2one |
| `loan_date` | DATE | Default today |
| `due_date` | DATE | Computed: loan_date + 14 days |
| `return_date` | DATE | Set when book is returned |
| `state` | VARCHAR | `borrowed` / `returned` / `overdue` |
| `is_overdue` | *(no col)* | Computed Boolean: `today > due_date and state == 'borrowed'` |
| `fine_amount` | NUMERIC | Computed: overdue days × daily rate |

---

### `library.book.category` → table `library_book_category`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR NOT NULL | e.g. "Fiction", "Science", "History" |
| `parent_id` | INTEGER FK → self | Self-referential Many2one — creates tree hierarchy |
| `child_ids` | *(no col)* | One2many reverse → children in hierarchy |

**Self-referential Many2one** (new pattern not in estate):
```python
parent_id = fields.Many2one("library.book.category", string="Parent Category")
child_ids = fields.One2many("library.book.category", "parent_id", string="Subcategories")
```
DB: `parent_id INTEGER FK → library_book_category(id)` (same table!)

---

### `library.return.wizard` (TransientModel — NO persistent table)

```python
class LibraryReturnWizard(models.TransientModel):
    _name = "library.return.wizard"
    # TransientModel rows are auto-deleted by a Odoo cron after 24h
```

| Field | Type | Purpose |
|---|---|---|
| `loan_id` | Many2one → library.loan | Which loan to return |
| `return_date` | Date | Optional: override return date |
| `fine_amount` | Float | Displayed for confirmation |
| `waive_fine` | Boolean | Should the fine be waived? |

**How wizards work in the View layer:**
- A button on the loan form triggers `type="action"` returning an `ir.actions.act_window` dict
- This opens the wizard as a modal popup form
- User fills in fields and clicks "Confirm Return"
- Python `action_confirm_return()` method processes the data and closes the wizard

---

## 🖥️ View Layer

### Book — Kanban View *(new concept)*
```xml
<kanban default_group_by="state">
    <field name="name"/>
    <field name="available_copies"/>
    <field name="cover_image" widget="image"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <img t-att-src="kanban_image()" .../>
                <strong><field name="name"/></strong>
                <p>Available: <field name="available_copies"/></p>
            </div>
        </t>
    </templates>
</kanban>
```
Cards grouped by `state` (Available / Unavailable / Archived) — draggable between columns.

### Loan — `@api.onchange` Example *(new concept)*
```python
@api.onchange("book_id")
def _onchange_book_id(self):
    """Runs in the BROWSER when user selects a book — before saving.
    Warns if the book has 0 available copies."""
    if self.book_id and self.book_id.available_copies == 0:
        return {
            'warning': {
                'title': "Book Unavailable",
                'message': f"'{self.book_id.name}' has no available copies."
            }
        }
```
`@api.onchange` → triggers a JSON-RPC to the server on field change, returns a `warning` dict shown as a yellow popup. **No DB write happens.**

### QWeb PDF Report *(new concept)*
```xml
<!-- ir.actions.report record -->
<record id="action_report_loan_slip" model="ir.actions.report">
    <field name="name">Loan Slip</field>
    <field name="model">library.loan</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">library.report_loan_slip_template</field>
</record>

<!-- QWeb template (HTML rendered to PDF by wkhtmltopdf) -->
<template id="report_loan_slip_template">
    <t t-call="web.html_container">
        <div class="page">
            <h2>Loan Slip — <t t-field="doc.member_id.partner_id.name"/></h2>
            <p>Book: <t t-field="doc.book_id.name"/></p>
            <p>Due: <t t-field="doc.due_date"/></p>
        </div>
    </t>
</template>
```

### Scheduled Action (Cron) *(new concept)*
```xml
<record id="ir_cron_check_overdue_loans" model="ir.cron">
    <field name="name">Library: Mark Overdue Loans</field>
    <field name="model_id" ref="model_library_loan"/>
    <field name="state">code</field>
    <field name="code">model.action_mark_overdue()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
</record>
```
Odoo scheduler runs `action_mark_overdue()` daily — updates loan states to `overdue`.

---

## 📁 File Structure

```
library/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── library_book_category.py   ← self-referential hierarchy
│   ├── library_book.py            ← _sql_constraints, Binary, ir.sequence
│   ├── library_member.py          ← partner delegation, ir.sequence
│   ├── library_loan.py            ← @api.onchange, computed fine, cron method
│   └── library_return_wizard.py   ← TransientModel
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── library_sequence_data.xml  ← ir.sequence records (auto-IDs)
│   └── library_cron_data.xml      ← scheduled action
├── report/
│   ├── library_loan_report.xml    ← ir.actions.report + QWeb template
│   └── library_loan_template.xml
└── views/
    ├── library_book_views.xml      ← tree, form, KANBAN, search
    ├── library_member_views.xml    ← tree, form, search
    ├── library_loan_views.xml      ← tree, form + wizard button
    ├── library_return_wizard_views.xml ← wizard popup form
    └── library_menus.xml
```

---
---

# 🍽️ Addon Idea 2: Restaurant Table Booking (`restaurant_booking`)

## What It Does

A restaurant management system where staff manage tables, customers make reservations, and the kitchen tracks active orders. A public booking form on the website lets customers self-book.

## New Odoo Concepts You'll Learn

| Concept | What It Is |
|---|---|
| **Calendar View** | Visual calendar showing bookings by date/time |
| **`_inherit` Model Inheritance** | Extending an existing Odoo model by adding fields to it |
| **`website` / Portal** | Exposing a form to unauthenticated/public users on `odoo.com/web` |
| **`res.config.settings` Extension** | Adding settings to the main Odoo Settings page |
| **`_rec_name`** | Control which field is shown as the display name in dropdowns |
| **`_order`** | Default sort order for records |
| **`digits` on Float** | Precise decimal control for prices |
| **`ir.rule` (Record Rules)** | Row-level security — e.g. customers only see their own bookings |
| **`_inherit = 'res.partner'`** | Adding a field to an Odoo built-in model without modifying core |

---

## 📊 DB Layer — All Tables

### `restaurant.table` → table `restaurant_table`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR NOT NULL | e.g. "Table 5", "Garden A" |
| `capacity` | INTEGER | Number of seats |
| `location` | VARCHAR | Selection: `indoor` / `outdoor` / `private` |
| `state` | VARCHAR | `available` / `occupied` / `reserved` / `maintenance` |
| `is_active` | BOOLEAN | Soft-delete via `active` field |
| `booking_ids` | *(no col)* | One2many → restaurant.booking |
| `color` | INTEGER | Color index for Kanban cards |

**`_rec_name` example:**
```python
_rec_name = "name"         # default — "Table 5" shown in dropdowns
# OR use a computed field:
display_name = fields.Char(compute="_compute_display_name")
# Then set _rec_name = "display_name"
# → "Table 5 (6 seats, Indoor)" shown in dropdowns
```

---

### `restaurant.booking` → table `restaurant_booking`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR | Auto-ref: `RES/2024/00001` via ir.sequence |
| `partner_id` | INTEGER FK → res_partner | Customer (Many2one) |
| `table_id` | INTEGER FK → restaurant_table | Which table (Many2one) |
| `guest_count` | INTEGER | Number of guests |
| `booking_date` | DATETIME | `fields.Datetime` — date + time |
| `duration` | FLOAT | Hours, e.g. 1.5 → 1h 30m |
| `end_time` | *(no col)* | Computed: `booking_date + duration hours` |
| `state` | VARCHAR | `draft` / `confirmed` / `seated` / `done` / `cancelled` |
| `notes` | TEXT | Special requests |
| `order_ids` | *(no col)* | One2many → restaurant.order |
| `total_amount` | *(no col)* | Computed: sum of order line totals |

**`_sql_constraints`** — prevent double-booking:
```python
_sql_constraints = [
    ('unique_table_time', 
     'UNIQUE(table_id, booking_date)',
     'This table is already booked at this time.'),
]
```

**`fields.Datetime`** (new vs. estate's `fields.Date`):
- Stores timezone-aware timestamp in the DB
- Shown with time picker in the UI
- Odoo auto-converts between user timezone and UTC for storage

---

### `restaurant.menu.item` → table `restaurant_menu_item`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR NOT NULL | Dish name |
| `category` | VARCHAR | Selection: `starter` / `main` / `dessert` / `drink` |
| `price` | NUMERIC(10,2) | `fields.Float(digits=(10,2))` — exactly 2 decimal places |
| `is_available` | BOOLEAN | Can be ordered today? |
| `description` | TEXT | — |
| `allergens` | VARCHAR | `fields.Many2many("restaurant.allergen")` |
| `image` | BYTEA | `fields.Image` — Odoo's image-specific Binary |

**`digits` parameter:**
```python
price = fields.Float(string="Price", digits=(10, 2))
```
→ PostgreSQL: `NUMERIC(10, 2)` — never rounds away centimes.

---

### `restaurant.order` → table `restaurant_order`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `booking_id` | INTEGER FK → restaurant_booking | Many2one |
| `line_ids` | *(no col)* | One2many → restaurant.order.line |
| `state` | VARCHAR | `draft` / `sent_to_kitchen` / `served` |
| `total_amount` | *(no col)* | Computed sum of line totals |

### `restaurant.order.line` → table `restaurant_order_line`

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `order_id` | INTEGER FK → restaurant_order | Many2one |
| `menu_item_id` | INTEGER FK → restaurant_menu_item | Many2one |
| `quantity` | INTEGER | Default 1 |
| `unit_price` | FLOAT | Copied from menu_item at time of order |
| `subtotal` | *(no col)* | Computed: `quantity × unit_price` |

---

### `_inherit = 'res.partner'` — extend existing model *(new concept)*

```python
class ResPartner(models.Model):
    _inherit = "res.partner"   # Extend, do NOT use _name
    
    # Adds this column to the existing res_partner table (ALTER TABLE)
    is_restaurant_customer = fields.Boolean(string="Restaurant Customer")
    preferred_table_id = fields.Many2one("restaurant.table", string="Preferred Table")
    booking_count = fields.Integer(compute="_compute_booking_count")
```

**DB impact:** `ALTER TABLE res_partner ADD COLUMN is_restaurant_customer BOOLEAN;`  
No new table is created — the existing `res_partner` table gains the columns.

---

### `ir.rule` — Record-Level Security *(new concept)*

```python
# In security XML:
# Customers can only see their OWN bookings (portal users)
<record id="rule_booking_portal_own_only" model="ir.rule">
    <field name="name">Booking: Portal users see own records only</field>
    <field name="model_id" ref="model_restaurant_booking"/>
    <field name="domain_force">[('partner_id.user_ids', 'in', [user.id])]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
</record>
```

This adds a **WHERE clause** to every SELECT on `restaurant_booking` for portal users:
```sql
SELECT * FROM restaurant_booking 
 WHERE partner_id IN (SELECT id FROM res_partner WHERE ... user = current_user)
```

---

## 🖥️ View Layer

### Calendar View *(new concept)*
```xml
<calendar string="Bookings"
          date_start="booking_date"
          date_stop="end_time"
          color="table_id"
          mode="week">
    <field name="partner_id"/>
    <field name="table_id"/>
    <field name="guest_count"/>
    <field name="state"/>
</calendar>
```
- Shows bookings as colored blocks on a weekly/monthly calendar
- `color="table_id"` → each table gets a unique color
- `date_start` / `date_stop` → event duration
- Click a slot to create a new booking with pre-filled time

### Booking Form with Status Bar Buttons
```
[Confirm] [Seat Guests] [Mark Done] [Cancel]
Draft ──── Confirmed ──── Seated ──── Done
```
Each button calls a Python method. `attrs=` hides irrelevant buttons per state.

### Website / Portal Form *(new concept)*
A `/booking` route added to the Odoo website lets customers book without logging in:
```python
# In a controller (controllers/main.py):
@http.route('/booking', auth='public', website=True)
def booking_page(self, **kwargs):
    tables = request.env['restaurant.table'].sudo().search([('state', '=', 'available')])
    return request.render('restaurant_booking.booking_form_template', {'tables': tables})
```
- `auth='public'` → no login required
- `website=True` → renders with the website header/footer
- QWeb template with standard HTML form POSTing back to Odoo

### `res.config.settings` Extension *(new concept)*
Adds fields to Odoo's main Settings page:
```python
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    default_booking_duration = fields.Float(
        string="Default Booking Duration (hours)",
        config_parameter="restaurant_booking.default_duration",
    )
    max_advance_days = fields.Integer(
        string="Max days in advance for bookings",
        config_parameter="restaurant_booking.max_advance",
    )
```
Values stored in `ir.config_parameter` (key-value store) — accessible anywhere via `self.env['ir.config_parameter'].get_param('restaurant_booking.default_duration')`.

---

## 📁 File Structure

```
restaurant_booking/
├── __manifest__.py              ← depends: ['base', 'website', 'mail']
├── __init__.py
├── controllers/
│   └── main.py                  ← /booking website route
├── models/
│   ├── __init__.py
│   ├── restaurant_table.py      ← _rec_name, _order, color field
│   ├── restaurant_booking.py    ← Datetime, _sql_constraints, computed totals
│   ├── restaurant_menu_item.py  ← digits on Float, fields.Image
│   ├── restaurant_order.py      ← order + lines pattern
│   ├── restaurant_allergen.py   ← simple lookup table
│   ├── res_partner.py           ← _inherit to extend res.partner
│   └── res_config_settings.py   ← _inherit to extend settings
├── security/
│   ├── ir.model.access.csv
│   └── restaurant_security.xml  ← ir.rule records
├── data/
│   └── restaurant_sequence.xml  ← ir.sequence for booking ref
├── views/
│   ├── restaurant_table_views.xml      ← kanban + form
│   ├── restaurant_booking_views.xml    ← tree + form + CALENDAR
│   ├── restaurant_menu_item_views.xml  ← kanban by category
│   ├── restaurant_order_views.xml      ← form with editable order lines
│   ├── res_config_settings_views.xml   ← settings page extension
│   └── restaurant_menus.xml
└── templates/
    └── booking_portal.xml       ← QWeb website template
```

---

## Comparison: What Each Addon Teaches

| Concept | estate | library | restaurant_booking |
|---|---|---|---|
| Basic CRUD model + fields | ✅ | ✅ | ✅ |
| Many2one / One2many / Many2many | ✅ | ✅ | ✅ |
| `@api.depends` computed | ✅ | ✅ | ✅ |
| `@api.constrains` | ✅ | ✅ | ✅ |
| `create()` ORM override | ✅ | ✅ | ✅ |
| Button actions | ✅ | ✅ | ✅ |
| Kanban View | ❌ | ✅ | ✅ |
| Calendar View | ❌ | ❌ | ✅ |
| TransientModel Wizard | ❌ | ✅ | ❌ |
| `@api.onchange` (pre-save UI) | ❌ | ✅ | ✅ |
| `ir.sequence` (auto IDs) | ❌ | ✅ | ✅ |
| Scheduled Cron Action | ❌ | ✅ | ❌ |
| QWeb PDF Report | ❌ | ✅ | ❌ |
| `_sql_constraints` (DB UNIQUE) | ❌ | ✅ | ✅ |
| `_inherit` model extension | ❌ | ❌ | ✅ |
| `ir.rule` record-level security | ❌ | ❌ | ✅ |
| Website / Public Portal | ❌ | ❌ | ✅ |
| `res.config.settings` extension | ❌ | ❌ | ✅ |
| Self-referential Many2one | ❌ | ✅ | ❌ |
| `fields.Datetime` | ❌ | ❌ | ✅ |
| `fields.Binary` / `fields.Image` | ❌ | ✅ | ✅ |
| `digits` on Float | ❌ | ❌ | ✅ |
