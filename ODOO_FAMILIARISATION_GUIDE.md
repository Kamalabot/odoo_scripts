# The Complete Odoo Developer Guide: Basics to Advanced

Welcome to the comprehensive guide for Odoo framework development! Now that you have hydrated a sandbox database (`ai_pf_db_clean`), you have a perfect playground. 

This guide will take you from the very fundamentals of Odoo's architecture to advanced server-side debugging and performance tuning.

---

## Part 1: Architecture & Fundamentals (The Basics)

### 1. The MVC-like Architecture
Odoo follows a multi-tier architecture similar to MVC (Model-View-Controller):
- **Model**: PostgreSQL database tables represented by Python ORM classes (`models/`).
- **View**: XML definitions (`views/`) combined with QWeb templating for the web client.
- **Controller**: Web controllers handling HTTP requests and routing (`controllers/`).

### 2. Module Structure (`__manifest__.py`)
Everything in Odoo is an addon module. A module dictates what is installed.
```python
# __manifest__.py
{
    'name': 'Custom Library Application',
    'version': '1.0',
    'category': 'Operations',
    'summary': 'Manage books, authors, and rentals',
    'depends': ['base', 'mail', 'website'], # Inherit logic from these modules!
    'data': [
        'security/ir.model.access.csv', # Security MUST be loaded first
        'views/book_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True, # Makes it show up as a main app icon
}
```

### 3. Developer Mode (The Most Important Tool)
Before writing any code, activate Developer Mode.
1. Go to **Settings** -> Scroll down to **Activate the developer mode**.
2. A bug icon `🐛` appears in the top menu.
3. **Hover Tooltips:** Hover over any field in Odoo (like "Customer" on a Sale Order) to see:
   - Field name (`partner_id`)
   - Object model (`res.partner`)
   - Field Type (`Many2one`)
4. **Edit View:** Click `🐛` -> **Edit View: Form** to extract the exact XML used to build the page you are on.

---

## Part 2: The ORM & Models (Intermediate)

Odoo handles all database operations through its powerful Object-Relational Mapper (ORM). You almost never write SQL.

### 1. Creating a Model
```python
from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'            # Creates 'library_book' table in Postgres
    _description = 'Library Book'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Adds Chatter/Notes to the bottom!

    # Basic Fields
    name = fields.Char(string='Title', required=True, tracking=True)
    active = fields.Boolean(default=True)
    publish_date = fields.Date(string='Published On')
    isbn = fields.Char(string='ISBN', help="13 Digit ISBN")
    
    # Advanced / Relational Fields
    author_id = fields.Many2one('res.partner', string='Author')
    category_ids = fields.Many2many('library.category', string='Tags')
```

### 2. Field Types Explained
- **`Char`, `Text`, `Html`**: String fields.
- **`Integer`, `Float`, `Monetary`**: Numeric fields. (Monetary requires a `currency_id` field).
- **`Boolean`, `Date`, `Datetime`**: Standard data types.
- **`Many2one`**: A foreign key to another model (e.g. linking to an Author).
- **`One2many`**: The inverse of Many2one (e.g. An author has many books).
- **`Many2many`**: Creates a join table automatically behind the scenes!

### 3. Recordsets & Environment (`self.env`)
In Odoo, `self` represents a **Recordset** (a list of records, which can be 1 or many).
You use `self.env` to interact with the database context and search other models.

```python
# Searching the database
partners = self.env['res.partner'].search([('is_company', '=', True)])
for partner in partners:
    print(partner.name)

# Creating a tracking log
self.env['mail.message'].create({
    'body': 'A new book was added!',
    'model': 'library.book',
    'res_id': self.id
})
```

---

## Part 3: XML Views & Injection (Intermediate)

Odoo builds frontend screens dynamically by injecting XML.

### 1. Actions & Menus
To make a model accessible, you need a Window Action and a Menu.
```xml
<!-- The Action: What happens when clicked? -->
<record id="action_library_book" model="ir.actions.act_window">
    <field name="name">Books</field>
    <field name="res_model">library.book</field>
    <field name="view_mode">kanban,tree,form</field>
</record>

<!-- The Menu: Where does the button live? -->
<menuitem id="menu_library_root" name="Library" sequence="10"/>
<menuitem id="menu_library_books" name="Books" parent="menu_library_root" action="action_library_book"/>
```

### 2. Modifying Existing Core Apps (`xpath`)
The most common task in Odoo is adding a custom field to an existing app (like Sales). **Never modify Odoo source code.** Instead, inherit the view and use `xpath` injection.

```xml
<record id="view_order_form_inherit_custom" model="ir.ui.view">
    <field name="name">sale.order.form.custom</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/> <!-- Target View -->
    <field name="arch" type="xml">
        <!-- Find the standard 'payment_term_id' field and insert ours before it -->
        <xpath expr="//field[@name='payment_term_id']" position="before">
            <field name="custom_delivery_instructions"/>
        </xpath>
    </field>
</record>
```

---

## Part 4: Business Logic & Controllers (Advanced)

### 1. Computing Fields (`@api.depends`)
Used to calculate fields on the fly (e.g., total price).
```python
price = fields.Float(string="Price")
tax = fields.Float(string="Tax")
total = fields.Float(string="Total", compute="_compute_total", store=True)

@api.depends('price', 'tax')
def _compute_total(self):
    for record in self:
        record.total = record.price + record.tax
```
*(Pro-tip: Adding `store=True` saves the computed value to PostgreSQL so it can be searched and grouped).*

### 2. Overriding Core ORM Methods (`create`, `write`)
You can intercept the exact moment records are born or updated.

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('isbn'):
            vals['isbn'] = 'PENDING-ISBN'
    # Call `super` to execute the original Odoo logic
    return super(LibraryBook, self).create(vals_list)
```

### 3. Controller Routing (Web Endpoints)
You can create standard HTTP APIs or Website pages via the `controllers/` directory.
```python
from odoo import http

class LibraryAPI(http.Controller):
    
    @http.route('/api/books', type='json', auth='user') # auth='public' for unauthenticated
    def get_books(self):
        books = http.request.env['library.book'].search([]) # request.env is like self.env
        return [{'id': b.id, 'title': b.name} for b in books]
```

---

## Part 5: Security & Automated Actions (Advanced)

### 1. Access Rights (`ir.model.access.csv`)
If this file is missing, nobody can see your new model!
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_book_user,library.book.user,model_library_book,base.group_user,1,1,1,0
access_book_manager,library.book.manager,model_library_book,base.group_system,1,1,1,1
```

### 2. Server Actions & Cron Jobs
You can run Python code on a schedule without modifying source files.
- Go to **Settings -> Technical -> Scheduled Actions** (Cron).
- Go to **Settings -> Technical -> Server Actions**.
You can trigger these actions over hundreds of selected records directly from the Odoo List View UI!

---

## Part 6: Performance & Debugging (Expert)

### 1. The N+1 Query Problem
When looping through recordsets, Odoo is lazy-loading. Accessing relational fields inside a loop executes a new SQL query *per iteration*.

**Bad (100 products = 100 queries):**
```python
for order in self:
    for line in order.order_line:
        print(line.product_id.name) 
```

**Good (Mapped pre-fetching):**
```python
# Extracts all products in a single SQL query!
products = self.mapped('order_line.product_id')
for product in products:
    print(product.name)
```

### 2. `pdb` and Logging
Use standard python debugging.
```python
import logging
_logger = logging.getLogger(__name__)

_logger.info("The book %s was rented by %s", self.name, self.partner_id.name)

# Drop a breakpoint in the Odoo console
import pdb; pdb.set_trace() 
```

### 3. `sudo()` vs User Context
Sometimes a user (like a portal customer) needs to trigger code that modifies an admin-level record. 
Using `.sudo()` completely bypasses all `ir.model.access` and `ir.rule` security checks for that specific operation.
```python
# If a public user clicks 'Submit Application', we sudo() to write to hr.applicant
self.env['hr.applicant'].sudo().create({'name': kwargs.get('name')})
```

---

## Final Project Recommendation

Start by building a standalone `hospital_management` module:
1. Create a `hospital.patient` model with `name`, `age`, and `gender`.
2. Create a `hospital.appointment` model linking `patient_id` to the patient, and `doctor_id` (`res.partner`).
3. View it: Build a Kanban view for Patients and a Calendar view for Appointments.
4. Logic: Write a compute field on `hospital.patient` that counts the total number of appointments they have had (`appointment_count`).
5. Web: Write an HTTP JSON controller that returns patient data.
