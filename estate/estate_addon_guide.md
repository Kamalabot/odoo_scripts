# 🏠 Estate Addon — Complete Guide (v2 with Business Logic)

---

## ✅ Bugs Fixed in v1 (Why the Addon Wasn't Loading)

All `<record>` tags in Odoo XML **require `<field name="...">` wrappers** — bare XML tags are ignored.

| File | Bug | Fix |
|---|---|---|
| `estate_property_views.xml` | `<model>`, `<name>`, `<arch>`, `<res_model>`, `<view_mode>`, `<help>` bare tags | All wrapped in `<field name="...">` |
| `estate_menus.xml` | `web_icon="base,..."` wrong module | Changed to `web_icon="estate,..."` |
| `static/description/` | Missing directory/icon | Created placeholder (replace with real PNG) |

> [!IMPORTANT]
> Replace `estate/static/description/icon.png` with a real 64×64 or 256×256 PNG.

---

## 📁 Addon File Structure (v2)

```
estate/
├── __manifest__.py                     ← Module metadata + data file load order
├── __init__.py                         ← Imports models/ package
├── models/
│   ├── __init__.py                     ← Imports all 4 model files in dependency order
│   ├── estate_property_type.py         ← NEW: Property type (Many2one source)
│   ├── estate_property_tag.py          ← NEW: Tags (Many2many with color)
│   ├── estate_property.py              ← UPDATED: + relational fields, computed, actions
│   └── estate_property_offer.py        ← NEW: Offer workflow with full business logic
├── security/
│   └── ir.model.access.csv             ← UPDATED: Added access for 3 new models
├── views/
│   ├── estate_property_type_views.xml  ← NEW: Type list + form
│   ├── estate_property_views.xml       ← UPDATED: Sell/Cancel + Offers tab + Tags
│   ├── estate_property_offer_views.xml ← NEW: Standalone offer list
│   └── estate_menus.xml                ← UPDATED: Settings > Property Types added
└── static/description/
    └── icon.png                        ← App switcher icon (replace with real PNG)
```

---

## 🧠 How the Addon Works

### Overall Architecture

```
Odoo Framework
│
├── ORM Layer          Python models → PostgreSQL tables (automatic migration)
├── View Layer         XML files → ir.ui.view records in DB → rendered in browser
├── Action Layer       ir.actions.act_window → links menus to model + views
└── Security Layer     ir.model.access.csv → per-model CRUD permissions
```

---

## 📊 Database Layer — All Models

### 1. `estate.property` → table `estate_property`

| Column | Type | Source |
|---|---|---|
| `id` | SERIAL PK | Odoo system |
| `name` | VARCHAR | `fields.Char` |
| `description` | TEXT | `fields.Text` |
| `postcode` | VARCHAR | `fields.Char` |
| `date_availability` | DATE | `fields.Date` |
| `expected_price` | NUMERIC | `fields.Float` |
| `selling_price` | NUMERIC | `fields.Float` (readonly) |
| `bedrooms` | INTEGER | `fields.Integer` |
| `living_area` | INTEGER | `fields.Integer` |
| `facades` | INTEGER | `fields.Integer` |
| `garage` | BOOLEAN | `fields.Boolean` |
| `garden` | BOOLEAN | `fields.Boolean` |
| `garden_area` | INTEGER | `fields.Integer` |
| `garden_orientation` | VARCHAR | `fields.Selection` |
| `state` | VARCHAR | `fields.Selection` |
| `active` | BOOLEAN | `fields.Boolean` |
| `property_type_id` | INTEGER FK | `fields.Many2one("estate.property.type")` |
| `active` | BOOLEAN | system |
| ~~`total_area`~~ | *(none)* | `fields.Integer(compute=...)` — no column |
| ~~`best_price`~~ | *(none)* | `fields.Float(compute=...)` — no column |
| ~~`tag_ids`~~ | *(none)* | `fields.Many2many` — junction table |
| ~~`offer_ids`~~ | *(none)* | `fields.One2many` — FK lives on offer side |

---

### 2. `estate.property.type` → table `estate_property_type`

| Column | Type | Source |
|---|---|---|
| `id` | SERIAL PK | Odoo system |
| `name` | VARCHAR NOT NULL | `fields.Char(required=True)` |

> [!NOTE]
> `property_ids` (One2many) has **no column** here. Odoo resolves it as:
> `SELECT * FROM estate_property WHERE property_type_id = <this.id>`

---

### 3. `estate.property.tag` → table `estate_property_tag`

| Column | Type | Source |
|---|---|---|
| `id` | SERIAL PK | Odoo system |
| `name` | VARCHAR NOT NULL | `fields.Char(required=True)` |
| `color` | INTEGER | `fields.Integer` (0–11 color palette) |

**Junction table auto-created by Odoo for the Many2many:**

`estate_property_tag_estate_property_rel(estate_property_id, estate_property_tag_id)`

SQL that Odoo runs when loading tags for a property:
```sql
SELECT tag.*
  FROM estate_property_tag tag
  JOIN estate_property_tag_estate_property_rel rel
       ON rel.estate_property_tag_id = tag.id
 WHERE rel.estate_property_id = <property.id>
```

---

### 4. `estate.property.offer` → table `estate_property_offer`

| Column | Type | Source |
|---|---|---|
| `id` | SERIAL PK | Odoo system |
| `price` | NUMERIC NOT NULL | `fields.Float(required=True)` |
| `status` | VARCHAR | `fields.Selection` (accepted/refused/null) |
| `partner_id` | INTEGER FK → res_partner | `fields.Many2one("res.partner")` |
| `property_id` | INTEGER FK → estate_property | `fields.Many2one("estate.property")` |
| `validity` | INTEGER | `fields.Integer(default=7)` |
| ~~`date_deadline`~~ | *(none)* | `fields.Date(compute=...)` — calculated dynamically |

---

### Relationship Diagram

```
estate.property.type          estate.property.tag
   id | name                     id | name | color
      │                                │
      │ Many2one (FK on property)      │ Many2many (junction table)
      │                                │
      └──────────┐       ┌────────────┘
                 ▼       ▼
            estate.property
     id | name | property_type_id | state | ...
                 │
                 │ One2many (FK on offer side)
                 ▼
         estate.property.offer
     id | price | status | partner_id | property_id | validity
```

---

## 🎯 Business Logic — All Operations

### Computed Fields (`@api.depends`)

| Field | On Model | Formula | Trigger |
|---|---|---|---|
| `total_area` | estate.property | `living_area + garden_area` | When either area field changes |
| `best_price` | estate.property | `max(offer_ids.price)` | When any offer's price changes |
| `date_deadline` | estate.property.offer | `create_date + validity days` | When validity or create_date changes |

**Key concept:** `@api.depends("offer_ids.price")` — the dot notation tells Odoo to watch the `price` field across **all related offer records**, not just the offer itself.

```python
@api.depends("offer_ids.price")
def _compute_best_price(self):
    for prop in self:
        prop.best_price = max(prop.offer_ids.mapped("price"), default=0)
```

### Inverse Field (`_inverse_date_deadline`)

The `inverse` parameter makes a computed field **editable** in the UI. When a user types a date in `date_deadline`, Odoo calls the inverse to back-calculate `validity`:

```python
def _inverse_date_deadline(self):
    for offer in self:
        base = offer.create_date.date() if offer.create_date else fields.Date.today()
        offer.validity = (offer.date_deadline - base).days
```

### Constraint (`@api.constrains`)

Runs after every save of the listed fields. If it raises `UserError`, the DB transaction is rolled back:

```python
@api.constrains("selling_price", "expected_price")
def _check_selling_price(self):
    for prop in self:
        if prop.selling_price > 0 and prop.selling_price < 0.9 * prop.expected_price:
            raise UserError("Selling price cannot be < 90% of expected price.")
```

### ORM Hook (`create()` override)

The `@api.model_create_multi` decorator wraps the standard `create()`:

```python
@api.model_create_multi
def create(self, vals_list):
    offers = super().create(vals_list)   # do the actual INSERT first
    for offer in offers:
        # then apply business rules
        if new offer price < current best:
            raise UserError(...)
        if property.state == 'new':
            property.state = 'offer_received'
    return offers
```

### Button Actions

| Button Label | XML `name=` | Model Method | Business Rule |
|---|---|---|---|
| **Sell** | `action_sell` | `estate.property` | Raises if state = canceled |
| **Cancel** | `action_cancel` | `estate.property` | Raises if state = sold |
| **✓ Accept** | `action_accept` | `estate.property.offer` | Sets selling_price + state; refuses siblings |
| **✗ Refuse** | `action_refuse` | `estate.property.offer` | Reverts selling_price + state if no accepted offer remains |

---

## 🖥️ View Layer — All Views

### Property Tree View
- **Color coding:** green rows = offer accepted; grey rows = sold
- **Columns:** name, type (Many2one), postcode, bedrooms, area, expected price, best offer, selling price, state, tag pills
- `best_price` is a computed field — shown read-only, updated live

### Property Form View

```
┌──────────────────────────────────────────────────────────────────┐
│  [Sell] [Cancel]          New ─── Offer Received ─── Offer Acc  │  ← header
├──────────────────────────────────────────────────────────────────┤
│  H1: Property Name                                   [Tag] [Tag] │  ← oe_title
│                                                                  │
│  Type: [dropdown]          Expected Price: [____]                │
│  Postcode: [____]          Best Offer: [readonly]                │
│  Available From: [date]    Selling Price: [readonly]             │
│                                                                  │
│  ┌──────────────┐  ┌───────────────────────────┐                │
│  │ Description  │  │          Offers            │                │
│  │ [fields...]  │  │ Price | Buyer | Deadline | │ ✓ ✗          │
│  │ Total Area:  │  │ ...                        │                │
│  └──────────────┘  └───────────────────────────┘                │
└──────────────────────────────────────────────────────────────────┘
```

### Property Search View
- Type in search bar → matches name, postcode, type, price, bedrooms
- "Available" filter button → `[('state', 'in', ('new', 'offer_received'))]`
- Group By postcode or Group By Property Type

### Property Type Form View
- Name field at top
- Inline One2many list of all properties of this type (demonstrates reverse navigation)

### Offer List View (standalone)
- Shows ALL offers across all properties
- Green rows = accepted, Red rows = refused

### Menu Structure

```
Real Estate [App Switcher]
├── Advertisements
│   ├── Properties         → opens estate.property tree/form
│   └── All Offers         → opens estate.property.offer list
└── Settings
    └── Property Types     → opens estate.property.type tree/form
```

---

## 🔄 Full Data Flow — Offer Acceptance Scenario

```
1. Agent opens a Property record
       ↓
   ORM: SELECT * FROM estate_property WHERE id = <N>
   ORM: SELECT * FROM estate_property_offer WHERE property_id = <N>
       ↓
2. Form renders with Offers tab showing all offers

3. Buyer submits a new offer (user types price + buyer in the Offers tab)
       ↓
   ORM: INSERT INTO estate_property_offer (price, partner_id, property_id, validity) VALUES (...)
   Hook: create() runs
     → checks existing best price
     → sets property.state = 'offer_received'
   ORM: UPDATE estate_property SET state = 'offer_received' WHERE id = <N>
   Computed: best_price recalculates → max of all offer prices

4. Agent clicks ✓ on the offer
       ↓
   RPC call → action_accept() method
     → siblings.write({'status': 'refused'})   ← batch UPDATE
     → offer.status = 'accepted'
     → property.selling_price = offer.price
     → property.state = 'offer_accepted'
   Constraint: _check_selling_price() fires → validates 90% rule
   Status bar in UI updates from "Offer Received" to "Offer Accepted"

5. Agent clicks Sell
       ↓
   RPC call → action_sell()
     → property.state = 'sold'
   Status bar shows "Sold"
   Tree view row turns grey (decoration-muted)
```

---

## ⚙️ How to Apply Changes to Odoo

After any code change, restart Odoo and upgrade the module:

```bash
# From inside your Odoo server directory:
python odoo-bin -c odoo.conf -u estate --stop-after-init
```

Or from the Odoo UI:
> Settings → Activate Developer Mode → Apps → search "estate" → Upgrade

> [!WARNING]
> If you changed model fields, Odoo runs `ALTER TABLE` automatically on upgrade.
> If you removed a field that has data, it will be dropped from the DB.
