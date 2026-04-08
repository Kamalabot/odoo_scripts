# 💡 Two Original Odoo Addon Ideas

> These are NOT on the Odoo App Store as core functionality.  
> They solve real problems that small/mid-size businesses face today.

---

## Why Not Library / Restaurant?

| Addon | Odoo App Store Status |
|---|---|
| Library Management | ✅ Multiple free modules (e.g. `library` by Cybrosys) |
| Restaurant Booking | ✅ Exists as `pos_restaurant`, `pos_table` in core |
| HR Leave Management | ✅ Core Odoo `hr_holidays` |
| Project Management | ✅ Core Odoo `project` |

The ideas below fill **actual gaps** in the ecosystem.

---

---

# ⚡ Addon Idea 1: Smart Energy & Utility Monitor (`energy_monitor`)

## The Problem It Solves

An office/factory pays ₹3–15 lakh/month in electricity bills. Nobody knows which department, floor, or machine is consuming the most. There's no tracking, no budget alerts, no trend analysis. Finance just pays the bill.

This addon lets facility/finance teams:
- Log monthly meter readings per department/floor
- Auto-calculate consumption and cost
- Set budgets and get alerts on overruns
- View trends via Graph and Pivot views (built-in Odoo analytics)
- Compare months / years / departments

## New Odoo Concepts Taught

| Concept | What It Is | Not in estate? |
|---|---|---|
| **Graph View** | Bar, Line, Pie charts directly in Odoo | ✅ New |
| **Pivot View** | Excel-like pivot table for analysis | ✅ New |
| **`fields.Monetary`** | Amount field tied to a currency | ✅ New |
| **`fields.Float` with `group_operator`** | Controls how Odoo aggregates in pivot (`sum`, `avg`) | ✅ New |
| **`_inherit = 'mail.thread'`** | Adds chatter (message log) + followers to any model | ✅ New |
| **`ir.config_parameter`** | App-wide settings stored as key-value pairs | ✅ New |
| **`res.config.settings` extension** | Adding your settings to the Odoo Settings page | ✅ New |
| **Automated Action (`base_automation`)** | Rule-based trigger: "if consumption > budget → send email" | ✅ New |

---

## 📊 DB Layer — All Tables

### `energy.meter` → table `energy_meter`

Represents a physical electricity/water/gas meter installed somewhere.

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR NOT NULL | "3rd Floor AC Circuit", "Factory Main Grid" |
| `ref` | VARCHAR | Meter serial number (from utility board) |
| `utility_type` | VARCHAR | Selection: `electricity` / `water` / `gas` / `diesel` |
| `unit` | VARCHAR | Selection: `kwh` / `litre` / `cubic_meter` / `litre` |
| `department_id` | INTEGER FK → hr.department | Many2one — which dept owns this meter |
| `location` | VARCHAR | Free text: "Server Room B2" |
| `rate` | NUMERIC | Cost per unit (₹/kWh) — `fields.Monetary` |
| `currency_id` | INTEGER FK → res.currency | Required by `fields.Monetary` |
| `monthly_budget` | NUMERIC | `fields.Monetary` — alert threshold |
| `reading_ids` | *(no col)* | One2many → energy.reading |
| `active` | BOOLEAN | Soft-delete |

**`fields.Monetary` pattern (new):**
```python
currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
rate = fields.Monetary(string="Rate per Unit", currency_field="currency_id")
```
→ PostgreSQL: Just stores a NUMERIC. The `currency_id` FK tells Odoo how to display/format it.

**`_inherit = 'mail.thread'` (new):**
```python
class EnergyMeter(models.Model):
    _name = "energy.meter"
    _inherit = ['mail.thread', 'mail.activity.mixin']
```
→ This does NOT create new tables. Instead it adds the chatter widget (message log + followers + scheduled activities) to the form view automatically. Data stored in `mail.message` and `mail.followers` tables.

---

### `energy.reading` → table `energy_reading`

One entry per meter per month — the manual reading entered by facility staff.

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `meter_id` | INTEGER FK → energy_meter | Many2one |
| `reading_date` | DATE NOT NULL | Date of reading |
| `meter_value` | FLOAT | Raw meter value (e.g. 04521.6 kWh) |
| `previous_value` | FLOAT | Computed: last reading's `meter_value` |
| `consumption` | FLOAT | Computed: `meter_value - previous_value` |
| `cost` | NUMERIC | Computed: `consumption × meter.rate` — `fields.Monetary` |
| `notes` | TEXT | Anomaly notes |
| `month` | VARCHAR | Computed: `"April 2024"` — used for grouping |
| `state` | VARCHAR | `draft` / `confirmed` / `disputed` |

**`group_operator` on Float (new):**
```python
consumption = fields.Float(
    string="Consumption",
    compute="_compute_consumption",
    store=True,                    # stored so pivot can aggregate it
    group_operator="sum",          # sum all consumptions in pivot table
)
cost = fields.Monetary(
    string="Cost",
    compute="_compute_cost",
    store=True,
    group_operator="sum",
)
```
Without `store=True`, the pivot view can't aggregate computed fields.  
`group_operator` tells Odoo whether to `sum`, `avg`, or `max` when grouping.

---

### `energy.budget.alert` — Automated Action (no dedicated model)

Instead of a model, this uses **Odoo's `base.automation` (Automated Actions)**:

```xml
<record id="automation_energy_budget_alert" model="base.automation">
    <field name="name">Alert: Energy Budget Exceeded</field>
    <field name="model_id" ref="model_energy_reading"/>
    <field name="trigger">on_write</field>           <!-- fires on every save -->
    <field name="filter_domain">
        [('cost', '>', meter_id.monthly_budget)]     <!-- condition -->
    </field>
    <field name="action_server_ids" eval="[...]"/>   <!-- send email action -->
</record>
```
When `cost > monthly_budget`, Odoo auto-sends an email to the department manager.  
This is done **entirely in XML** — no Python method needed.

---

### `ir.config_parameter` Usage (new)

Instead of a dedicated model, global settings are stored in Odoo's built-in key-value store:

```python
# In res.config.settings extension:
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    energy_alert_email = fields.Char(
        string="Alert Email",
        config_parameter="energy_monitor.alert_email",
    )
    default_rate_electricity = fields.Float(
        string="Default Electricity Rate (₹/kWh)",
        config_parameter="energy_monitor.default_rate_elec",
    )

# Reading the value anywhere:
rate = self.env['ir.config_parameter'].sudo().get_param('energy_monitor.default_rate_elec')
```
DB: Values stored in `ir_config_parameter(key, value)` — a simple key-value table already in Odoo.

---

## 🖥️ View Layer

### Graph View *(completely new concept)*

```xml
<record id="energy_reading_view_graph" model="ir.ui.view">
    <field name="name">energy.reading.graph</field>
    <field name="model">energy.reading</field>
    <field name="arch" type="xml">
        <!--
            type="bar" | "line" | "pie"
            @type on measure fields: "measure" = numeric value to plot
            @type="col" on fields: used as X axis
            Default grouping: month → bar chart of monthly consumption
        -->
        <graph string="Energy Consumption" type="bar">
            <field name="month" type="col"/>
            <field name="consumption" type="measure"/>
            <field name="cost" type="measure"/>
        </graph>
    </field>
</record>
```
User sees a bar chart. They can switch to Line or Pie. They can group by `meter_id`, `department_id`, `utility_type` in the UI.

### Pivot View *(completely new concept)*

```xml
<record id="energy_reading_view_pivot" model="ir.ui.view">
    <field name="name">energy.reading.pivot</field>
    <field name="model">energy.reading</field>
    <field name="arch" type="xml">
        <!--
            type="row": shows in row headers (group by dept)
            type="col": shows in column headers (group by month)
            type="measure": the numeric value in cells
        -->
        <pivot string="Consumption Analysis">
            <field name="meter_id" type="row"/>
            <field name="month" type="col"/>
            <field name="consumption" type="measure"/>
            <field name="cost" type="measure"/>
        </pivot>
    </field>
</record>
```
This renders an interactive Excel-style pivot table: departments as rows, months as columns, consumption and cost in cells. Fully expandable/collapsible in the UI.

### View Mode Order (includes 2 new types)
```xml
<field name="view_mode">tree,form,graph,pivot</field>
```

### Chatter on Reading Form

Because of `_inherit = ['mail.thread']`, adding this to the form XML is enough:
```xml
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```
This gives every reading record a full message log — staff can post "meter was stuck, reading estimated" notes that are timestamped and tied to the record.

---

## 📁 File Structure

```
energy_monitor/
├── __manifest__.py              ← depends: ['base', 'mail', 'base_automation', 'hr']
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── energy_meter.py          ← mail.thread, Monetary, ir.config_parameter
│   ├── energy_reading.py        ← computed cost/consumption, store=True, group_operator
│   └── res_config_settings.py  ← settings extension
├── security/
│   └── ir.model.access.csv
├── data/
│   └── energy_automation.xml   ← base.automation budget alert rule
├── views/
│   ├── energy_meter_views.xml  ← tree, form (with chatter)
│   ├── energy_reading_views.xml ← tree, form, GRAPH, PIVOT
│   ├── res_config_settings_views.xml
│   └── energy_menus.xml
```

---
---

# 🎯 Addon Idea 2: Team OKR Tracker (`team_okrs`)

## The Problem It Solves

OKR (Objectives & Key Results) is the goal-setting framework used by Google, Intel, Spotify. Teams set quarterly goals, define measurable key results, and do weekly check-ins. No good Odoo module exists for this — companies either use Notion/Asana (disconnected from their ERP data) or spreadsheets.

This addon lets companies:
- Create Company → Team → Individual OKRs in a hierarchy
- Track % progress on each Key Result
- Do weekly check-ins with confidence scores and blockers
- See company-wide alignment: which individual OKRs support which team OKRs
- Auto-close quarters and roll-forward incomplete objectives

## New Odoo Concepts Taught

| Concept | What It Is | Not in estate? |
|---|---|---|
| **`_inherit = 'mail.thread'`** | Chatter/messaging on records | ✅ New |
| **`_inherit = 'mail.activity.mixin'`** | Scheduled activities (reminders) | ✅ New |
| **`fields.Float` as `widget="progressbar"`** | Renders float 0-100 as a progress bar in UI | ✅ New |
| **`fields.Html`** | Rich-text HTML field (WYSIWYG editor in form) | ✅ New |
| **`_parent_name` / hierarchy** | Nested records (Company OKR → Team OKR → Individual OKR) | ✅ New |
| **`@api.model` class method** | Method called on model (not a record) — for scheduled quarter close | ✅ New |
| **`fields.Reference`** | Polymorphic FK — can point to different models (dynamic Many2one) | ✅ New |
| **`ir.rule` user-scoped** | Each user sees only their team's OKRs by default | ✅ New |
| **`fields.Integer` as `widget="priority"`** | Star ★★★ rating widget | ✅ New |

---

## 📊 DB Layer — All Tables

### `okr.objective` → table `okr_objective`

One objective = one high-level goal ("Grow revenue by 30%", "Launch mobile app").

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR NOT NULL | The objective statement |
| `description` | TEXT (HTML) | `fields.Html` — rich text with formatting |
| `owner_id` | INTEGER FK → res.users | Who owns this objective |
| `team_id` | INTEGER FK → hr.team | Which team (or NULL for company-level) |
| `period_id` | INTEGER FK → okr.period | Which quarter (Q1 2024, Q2 2024) |
| `parent_id` | INTEGER FK → self | Another objective this aligns to (hierarchy) |
| `child_ids` | *(no col)* | One2many reverse → child objectives |
| `key_result_ids` | *(no col)* | One2many → okr.key_result |
| `level` | VARCHAR | Selection: `company` / `team` / `individual` |
| `state` | VARCHAR | `draft` / `active` / `completed` / `cancelled` |
| `progress` | FLOAT | Computed from key results — shown as progress bar |
| `priority` | INTEGER | `fields.Integer(widget="priority")` → star rating 0-3 |
| `color` | INTEGER | Color of the Kanban card |

**`fields.Html` (new):**
```python
description = fields.Html(string="Description")
```
→ PostgreSQL: Stores raw HTML as TEXT.  
→ View: Renders a full WYSIWYG editor (bold, bullets, links) in the form.

**`fields.Integer` as priority widget (new):**
```python
priority = fields.Integer(string="Priority", default=0)
```
In the view: `<field name="priority" widget="priority"/>` → renders ★☆☆ star rating.

---

### `okr.key_result` → table `okr_key_result`

The measurable part. Every objective has 2-5 key results.

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR NOT NULL | "Reach 10,000 monthly active users" |
| `objective_id` | INTEGER FK → okr_objective | Many2one (required) |
| `target_value` | FLOAT | 10000 (the goal) |
| `current_value` | FLOAT | 6200 (where we are now) |
| `start_value` | FLOAT | 3000 (where we started) |
| `progress` | FLOAT | Computed: `(current - start) / (target - start) × 100` |
| `unit` | VARCHAR | "users", "%", "₹ lakh", "NPS points" |
| `owner_id` | INTEGER FK → res.users | Who drives this KR |
| `confidence` | INTEGER | Selection 1-5: how confident we'll hit it |
| `check_in_ids` | *(no col)* | One2many → okr.check_in |
| `state` | VARCHAR | `on_track` / `at_risk` / `off_track` / `done` |

**Computed progress stored for aggregation:**
```python
@api.depends("current_value", "target_value", "start_value")
def _compute_progress(self):
    for kr in self:
        span = kr.target_value - kr.start_value
        if span:
            kr.progress = min(100.0, (kr.current_value - kr.start_value) / span * 100)
        else:
            kr.progress = 0.0
```

---

### `okr.check_in` → table `okr_check_in`

Weekly pulse entry for a Key Result.

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `key_result_id` | INTEGER FK → okr_key_result | Many2one |
| `check_in_date` | DATE | Default today |
| `value` | FLOAT | Current value this week |
| `confidence` | INTEGER | Selection 1-5 |
| `note` | TEXT (HTML) | `fields.Html` — blockers, context |
| `owner_id` | INTEGER FK → res.users | Who submitted this check-in |

---

### `okr.period` → table `okr_period`

Defines a quarter or half-year window.

| Column | Type | Notes |
|---|---|---|
| `id` | SERIAL PK | — |
| `name` | VARCHAR | "Q2 2024", "H1 2025" |
| `date_start` | DATE | — |
| `date_end` | DATE | — |
| `state` | VARCHAR | `upcoming` / `active` / `closed` |
| `objective_ids` | *(no col)* | One2many → okr_objective |

**`@api.model` class method for scheduled close (new):**
```python
@api.model
def action_close_expired_periods(self):
    """
    @api.model: called on the MODEL CLASS, not a specific record.
    No 'self' loop — this is a class-level operation.
    Called by a daily cron job.
    """
    today = fields.Date.today()
    expired = self.search([('date_end', '<', today), ('state', '=', 'active')])
    expired.write({'state': 'closed'})
    # Notify all objective owners
    for period in expired:
        period.objective_ids.mapped('owner_id').notify_period_closed(period)
```

---

### `fields.Reference` — Polymorphic Link (new)

The "aligned to" field on an objective can point to another objective OR a project OR a company strategy item. This uses `fields.Reference`:

```python
aligned_to = fields.Reference(
    selection=[
        ('okr.objective', 'OKR Objective'),
        ('project.project', 'Project'),
    ],
    string="Aligned To",
)
```
→ PostgreSQL: Stores as `aligned_to_type VARCHAR, aligned_to_id INTEGER` — two columns together form the polymorphic key.  
→ View: Renders as a dropdown that first asks "which model?" then "which record?"

---

### `ir.rule` — User-Scoped Visibility (new)

```xml
<!-- Individual users only see OKRs where they are the owner OR their team is the owner -->
<record id="rule_okr_user_own" model="ir.rule">
    <field name="name">OKR: Users see own + team objectives</field>
    <field name="model_id" ref="model_okr_objective"/>
    <field name="domain_force">
        ['|', ('owner_id', '=', user.id), ('team_id.member_ids', 'in', [user.id])]
    </field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- Managers see everything -->
<record id="rule_okr_manager_all" model="ir.rule">
    <field name="name">OKR: Managers see all</field>
    <field name="model_id" ref="model_okr_objective"/>
    <field name="domain_force">[(1, '=', 1)]</field>  <!-- no filter -->
    <field name="groups" eval="[(4, ref('base.group_user_manager'))]"/>
</record>
```

---

## 🖥️ View Layer

### Objective — Kanban View by State
Cards grouped by `state`:  
`Draft → Active → Completed / Cancelled`

Each card shows:
- Objective name
- Progress bar (% from key results)
- Owner avatar
- Priority stars ★★★
- Color-coded by confidence (green/yellow/red)

### Key Result — Inline Editable Tree on Objective Form
```
┌─────────────────────────────────────────────────────────────────┐
│  Objective: "Reach 1M ARR"           ★★★  [Active]  [Progress] │
│                                                                 │
│  Key Results:                                                   │
│  ┌──────────────────────────┬───────┬───────┬──────┬─────────┐ │
│  │ Key Result               │ Start │ Target│ Now  │Progress │ │
│  ├──────────────────────────┼───────┼───────┼──────┼─────────┤ │
│  │ Monthly Revenue          │ 60L   │ 100L  │ 72L  │ ███░ 30%│ │
│  │ New Enterprise Customers │ 5     │ 20    │ 9    │ ██░░ 27%│ │
│  │ Churn Rate below 2%      │ 4.2%  │ 2.0%  │ 3.1% │ ██░░ 50%│ │
│  └──────────────────────────┴───────┴───────┴──────┴─────────┘ │
│                                                                 │
│  [Add Check-in for selected KR]                                 │
│  ─────────────────────────────────────────────────────────     │
│  💬 Chatter: "Q2 off to a slow start — pipeline review Fri"    │
└─────────────────────────────────────────────────────────────────┘
```

### Progress Bar Widget (new)

```xml
<!-- On the key_result list inside objective form: -->
<field name="progress" widget="progressbar"/>
<!-- Renders as a filled bar: ████░░░ 68% -->

<!-- On the objective form itself: -->
<field name="progress" widget="progressbar" options="{'max_value': 100, 'editable': false}"/>
```

### Priority Widget (new)
```xml
<field name="priority" widget="priority"/>
<!-- Renders as clickable stars: ★★☆ -->
```

### Graph View — OKR Dashboard
```xml
<graph type="bar">
    <field name="team_id" type="row"/>
    <field name="progress" type="measure"/>
</graph>
```
Bar chart: teams on X axis, average OKR progress % on Y axis.

### Pivot View — Cross-Quarter Analysis
```xml
<pivot>
    <field name="period_id" type="col"/>
    <field name="team_id" type="row"/>
    <field name="progress" type="measure"/>
</pivot>
```
Rows = teams, columns = Q1/Q2/Q3/Q4, cells = average completion %.

---

## 📁 File Structure

```
team_okrs/
├── __manifest__.py            ← depends: ['base', 'mail', 'hr']
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── okr_period.py          ← @api.model cron method, scheduled close
│   ├── okr_objective.py       ← mail.thread, fields.Html, fields.Reference, hierarchy
│   ├── okr_key_result.py      ← computed progress, progressbar, store=True
│   └── okr_check_in.py        ← check-in pulse entries
├── security/
│   ├── ir.model.access.csv
│   └── okr_security.xml       ← ir.rule for user/manager scoping
├── data/
│   └── okr_cron.xml           ← scheduled action for period auto-close
├── views/
│   ├── okr_period_views.xml   ← simple list + form
│   ├── okr_objective_views.xml ← KANBAN + form with inline KRs + chatter
│   ├── okr_key_result_views.xml ← progressbar widget, priority widget
│   ├── okr_check_in_views.xml  ← form with Html note, GRAPH trend
│   └── okr_menus.xml
```

---

## Comparison: New Concepts in Each

| Concept | estate | energy_monitor | team_okrs |
|---|---|---|---|
| `fields.Monetary` + currency | ❌ | ✅ | ❌ |
| Graph View (bar/line/pie) | ❌ | ✅ | ✅ |
| Pivot View (cross-tab) | ❌ | ✅ | ✅ |
| `mail.thread` (chatter) | ❌ | ✅ | ✅ |
| `ir.config_parameter` settings | ❌ | ✅ | ❌ |
| `base.automation` (no-code rule) | ❌ | ✅ | ❌ |
| `fields.Html` (rich text) | ❌ | ❌ | ✅ |
| `widget="progressbar"` | ❌ | ❌ | ✅ |
| `widget="priority"` (stars) | ❌ | ❌ | ✅ |
| `fields.Reference` (polymorphic) | ❌ | ❌ | ✅ |
| `@api.model` class method | ❌ | ❌ | ✅ |
| `ir.rule` per-user scoping | ❌ | ❌ | ✅ |
| Scheduled Cron | ❌ | ✅ | ✅ |
| Self-referential hierarchy | ❌ | ❌ | ✅ |
| `store=True` computed (for pivot) | ❌ | ✅ | ✅ |
