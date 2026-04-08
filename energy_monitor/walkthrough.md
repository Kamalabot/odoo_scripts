# Smart Energy & Utility Monitor — Addon Walkthrough

**Module:** `energy_monitor`  
**Odoo Version:** 17+  
**Author:** Antigravity  
**License:** LGPL-3

---

## Overview

The `energy_monitor` addon enables facility and finance teams to track utility consumption (electricity, water, gas, diesel) and associated costs per meter per department. It integrates with Odoo's HR, Mail, and Base Automation modules for a complete workflow — from reading entry, to budget alerting, to trend analysis.

---

## Architecture

```
energy_monitor/
├── __manifest__.py              # Module metadata and file load order
├── __init__.py                  # Imports models package
├── models/
│   ├── __init__.py              # Imports all three models
│   ├── energy_meter.py          # Master meter record (EnergyMeter)
│   ├── energy_reading.py        # Monthly reading log (EnergyReading)
│   └── res_config_settings.py  # Extends global settings
├── views/
│   ├── energy_menus.xml         # Top-level & sub-menu definitions
│   ├── energy_meter_views.xml   # Tree + Form + Action for meters
│   ├── energy_reading_views.xml # Tree + Form + Graph + Pivot + Action
│   └── res_config_settings_views.xml  # Settings panel extension
├── security/
│   ├── energy_security.xml      # Module category + User/Manager groups
│   └── ir.model.access.csv      # Model-level CRUD permissions
└── data/
    └── energy_automation.xml    # Automated budget-exceeded alert
```

---

## Models

### `energy.meter` — Master Meter Record

**File:** `models/energy_meter.py`

Represents a physical utility meter installed at a location/department.

| Field | Type | Description |
|---|---|---|
| `name` | Char | Meter display name (required) |
| `ref` | Char | Serial/reference number |
| `utility_type` | Selection | electricity / water / gas / diesel |
| `unit` | Selection | kWh / Litre / Cubic Meter |
| `department_id` | Many2one → `hr.department` | Owning department |
| `location` | Char | Physical location string |
| `currency_id` | Many2one → `res.currency` | Defaults to company currency |
| `rate` | Monetary | Cost per unit (used for cost calculation) |
| `monthly_budget` | Monetary | Threshold for budget alert automation |
| `reading_ids` | One2many → `energy.reading` | All readings for this meter |
| `active` | Boolean | Supports archive/unarchive |

Inherits `mail.thread` and `mail.activity.mixin` for chatter and activity tracking.

---

### `energy.reading` — Monthly Reading Log

**File:** `models/energy_reading.py`

Records actual meter readings and computes consumption/cost automatically.

| Field | Type | Description |
|---|---|---|
| `meter_id` | Many2one → `energy.meter` | The meter this reading belongs to |
| `reading_date` | Date | Date of the reading |
| `meter_value` | Float | Raw meter value (current) |
| `previous_value` | Float (computed) | Last reading value for same meter |
| `consumption` | Float (computed) | `meter_value - previous_value` |
| `currency_id` | Many2one (related) | Pulled from meter |
| `cost` | Monetary (computed) | `consumption × meter rate` |
| `month` | Char (computed) | e.g. `"April 2026"` (for grouping) |
| `state` | Selection | draft / confirmed / disputed |
| `notes` | Text | Free-text anomaly notes |

**Key computed field logic:**

- `_compute_consumption`: Searches for the most recent reading of the **same meter** before the current `reading_date` and treats it as the `previous_value`. Uses `order='reading_date desc, id desc'` for deterministic ordering.
- `_compute_cost`: Multiplies stored `consumption` by `meter_id.rate`.
- `_compute_month`: Formats `reading_date` as `"%B %Y"` string for pivot/graph grouping.

---

### `res.config.settings` — Global Configuration

**File:** `models/res_config_settings.py`

Extends Odoo's standard settings form to expose two module-level parameters:

| Config Parameter | Field | Purpose |
|---|---|---|
| `energy_monitor.alert_email` | `energy_alert_email` | Email address to notify on budget overruns |
| `energy_monitor.default_rate_elec` | `default_rate_electricity` | Global default rate for electricity meters |

> [!NOTE]
> The `alert_email` field is stored using `config_parameter` (ir.config_parameter). It is **not** currently wired into the automation action — the automation instead assigns a mail activity to the department manager. This email field is available for future custom email template integration.

---

## Views & Menus

### Menu Structure

```
Facility (sequence 50)
├── Energy Management (sequence 10)
│   ├── Meters          → action_energy_meter
│   └── Readings        → action_energy_reading
└── Configuration (sequence 100)
    └── Energy Settings → action_energy_config_settings
```

### Meter Views (`energy_meter_views.xml`)

- **Tree**: Shows name, utility type, department, rate, budget.
- **Form**: Two-column layout with `oe_title` for name, reference, type, unit, department, location, rate, budget, and `active` toggle. Chatter included.
- `currency_id` hidden in both views but present for `monetary` widget rendering.

### Reading Views (`energy_reading_views.xml`)

- **Tree**: Color-coded rows — blue for draft, green for confirmed, orange for disputed. Displays meter, date, month, consumption, cost, and status badge.
- **Form**: `statusbar` header for state transitions. Shows previous value, current meter value, computed consumption and cost. Notebook for notes. Chatter included.
- **Graph**: Bar chart grouping by month (columns) and meter (rows), measuring consumption and cost.
- **Pivot**: Cross-tab analysis with meters as rows, months as columns, and consumption/cost as measures.

### Settings View (`res_config_settings_views.xml`)

Extends `base.res_config_settings_view_form` via XPath. Adds an `<app>` block named `energy_monitor` with two setting fields: alert email and default electricity rate.

---

## Security

### Groups (`security/energy_security.xml`)

| Group | Inherits | Access |
|---|---|---|
| `group_energy_user` | `base.group_user` | Read meters, create/edit readings |
| `group_energy_manager` | `group_energy_user` | Full CRUD on meters and readings + settings |

### Access Control List (`ir.model.access.csv`)

| Record | Model | Group | R | W | C | D |
|---|---|---|---|---|---|---|
| `access_energy_meter_user` | `energy.meter` | Energy User | ✓ | — | — | — |
| `access_energy_reading_user` | `energy.reading` | Energy User | ✓ | ✓ | ✓ | — |
| `access_energy_meter_manager` | `energy.meter` | Energy Manager | ✓ | ✓ | ✓ | ✓ |
| `access_energy_reading_manager` | `energy.reading` | Energy Manager | ✓ | ✓ | ✓ | ✓ |
| `access_res_config_settings` | `res.config.settings` | `base.group_system` | ✓ | ✓ | ✓ | ✓ |

---

## Automation (`data/energy_automation.xml`)

Wrapped in `<data noupdate="1">` so it is only loaded on first install.

**Trigger:** `on_create_or_write` on `energy.reading`

**Server Action (`action_energy_budget_exceeded`):**
- Checks if `record.cost > record.meter_id.monthly_budget` AND budget is > 0.
- Creates a `mail.activity` of type `mail.mail_activity_data_warning` on the parent **meter**, assigned to the department manager (falls back to current user if no manager is set).
- Activity summary: `"Budget Exceeded Alert"` with a note including date, cost and budget values.

---

## Code Review Findings & Recommended Fixes

### 🔴 Bug — `_compute_consumption` Origin ID Handling

**File:** `models/energy_reading.py` — line 43

```python
# Current (fragile)
('id', '!=', record._origin.id if record._origin.id else getattr(record, 'id', False))
```

This pattern can behave unexpectedly when `_origin.id` is `0` (falsy). Use a cleaner guard:

```python
# Recommended
exclude_id = record._origin.id or record.id or False
if exclude_id:
    domain.append(('id', '!=', exclude_id))
```

### 🟡 Issue — `month` as `Char` causes non-deterministic sorting

Group-by operations on `month` (e.g. "April 2026", "March 2026") sort alphabetically, not chronologically. Consider adding a stored `Date` helper field:

```python
month_start = fields.Date(
    string="Month Start",
    compute="_compute_month",
    store=True,
    group_operator=False
)
```

And compute both `month` (display) and `month_start` (for ordering) in `_compute_month`.

### 🟡 Issue — No `_order` defined on `energy.reading`

Without a default sort, readings are ordered by `id`. Add this to the model class:

```python
_order = "reading_date desc, id desc"
```

### 🟡 Issue — `res_name` deprecated in `mail.activity.create`

In `energy_automation.xml` line 13, `res_name` is no longer a standard field on `mail.activity` in Odoo 17. Remove it — the ORM derives it from `res_model_id` and `res_id` automatically.

### 🟢 Improvement — Meter Form missing `reading_ids` tab

The `energy_meter_views.xml` form does not show related readings inline. Add a notebook tab:

```xml
<notebook>
    <page string="Readings" name="readings_page">
        <field name="reading_ids" readonly="1">
            <tree>
                <field name="reading_date"/>
                <field name="meter_value"/>
                <field name="consumption"/>
                <field name="cost" widget="monetary"/>
                <field name="state" widget="badge"/>
            </tree>
        </field>
    </page>
</notebook>
```

### 🟢 Improvement — `version` should follow Odoo convention

Change manifest `'version': '1.0'` → `'version': '17.0.1.0.0'` to be compatible with OCA and standard Odoo module versioning.

---

## Installation

```bash
# 1. Place the module in your Odoo addons path
cp -r energy_monitor /path/to/odoo/addons/

# 2. Restart the Odoo service
sudo systemctl restart odoo

# 3. Update the module list
# In Odoo: Apps → Update Apps List

# 4. Search for "Smart Energy" and click Install
```

---

## Post-Install Setup

1. **Assign Users to Security Groups**
   - Enable Developer Mode: Settings → General Settings → Activate Developer Mode
   - Go to Settings → Users & Companies → Users
   - Select a user → Access Rights tab → **Energy Management** section
   - Set to `User` (read + log readings) or `Manager` (full access)

2. **Configure Global Settings**
   - Go to Facility → Configuration → Energy Settings
   - Set the default electricity rate and alert email

3. **Create Meters**
   - Go to Facility → Energy Management → Meters
   - Click **New**, fill in name, utility type, unit, department, rate, and budget
   - Save and optionally archive decommissioned meters

4. **Log Readings**
   - Go to Facility → Energy Management → Readings
   - Click **New**, select the meter and reading date, enter the current meter value
   - Consumption and cost auto-compute on save
   - Confirm the reading to change state from `draft` → `confirmed`

5. **Analyze Trends**
   - In the Readings list view, switch to **Graph** or **Pivot** view
   - Use the Group By options to slice by month, meter, or department

---

## Dependencies

| Module | Purpose |
|---|---|
| `base` | Core Odoo framework |
| `mail` | Chatter, mail threads, and activity types |
| `base_automation` | Automated action triggers |
| `hr` | Department model for meter assignment |
