# 🎯 Team OKR Tracker (`okrmetrics`) — Walkthrough

I have successfully built the `okrmetrics` addon from scratch. This new addon enables tracking of Objectives and Key Results in Odoo and teaches several advanced concepts that go far beyond standard models and views.

## 📁 Architecture & File Layout

The module follows Odoo's standard layout and separates logic into four main models:

```
okrmetrics/
├── __manifest__.py                 ← Depends on base, mail, and hr
├── __init__.py                     
├── models/
│   ├── __init__.py
│   ├── okr_period.py               ← Manages Quarters/Halfs (Q1, Q2)
│   ├── okr_objective.py            ← High-level goals (e.g. "Launch New App")
│   ├── okr_key_result.py           ← Measurable targets inside an Objective
│   └── okr_check_in.py             ← Weekly pulse logs on Key Results
├── security/
│   ├── ir.model.access.csv         ← Basic CRUD rights
│   └── okr_security.xml            ← Record Level Security via ir.rule
├── data/
│   └── okr_cron.xml                ← Scheduled actions to close old periods
├── views/
│   ├── okr_period_views.xml
│   ├── okr_objective_views.xml     ← Complex Kanban, Forms & Trees
│   └── okr_menus.xml               
└── static/description/icon.png     ← App Switcher icon
```

---

## 🚀 Key Advanced Concepts Demonstrated

This build introduces several new features to the Odoo ecosystem:

### 1. The Chatter (`mail.thread`)
Added easily to `# models/okr_objective.py`, the chatter enables teams to discuss OKRs directly on the record, @mention users, and track activity history.
```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```
To show it in the UI, we just added `<div class="oe_chatter">...</div>` at the bottom of the form view.

### 2. Widget Enhancements 
- **`widget="progressbar"`**: Visualizes completion from 0-100. We utilized this on Key Results and rolled it up to Objectives.
- **`widget="priority"`**: Adds interactive star ratings to Objective forms for quick prioritization tracking.
- **`fields.Html`**: Replaces the standard Text field with a fully functional WYSIWYG editor so descriptions can have bullet points and links.

### 3. Record Rules (`ir.rule`)
Located in `security/okr_security.xml`. This limits what users can see!
Standard employees are restricted by a `domain_force` to only see Objectives where they are the owner, or where their assigned department is the owner.

### 4. Scheduled Actions (Cron Jobs)
In `data/okr_cron.xml`, we instruct Odoo to wake up every 1 day and run `action_close_expired_periods()`.
The function in `models/okr_period.py` uses the `@api.model` decorator, meaning it runs iteratively across records at the database level rather than on the UI.

### 5. Polymorphic Relations (`fields.Reference`)
In `okr_objective.py`, the `aligned_to` field can point to totally different models! Instead of just being a `Many2one` targeting another Objective, the user can choose the type of reference first (e.g., another Objective or a particular User).

---

## 🔄 Data Execution Flow (How it runs)

1. A manager creates an **OKR Period** (e.g., Q1 2024).
2. Users create **Objectives** assigned to that Period.
3. Users add inline **Key Results**, defining `start_value` and `target_value`.
4. Over time, employees log **Check-ins** against Key Results.
5. The `create()` hook inside `okr_check_in.py` automatically updates the parent `Key Result`'s `current_value` and `confidence` to match the latest check-in.
6. The Key Result dynamically recomputes its own `progress`.
7. Because it's computed to `store=True`, the parent Objective detects that dependent values changed, and immediately updates its own over-all `progress` bar.

---

## 🛠️ Step-by-Step Testing Guide

To test out these concepts on your machine:

1. In your Odoo environment, update the apps list.
```sh
odoo-bin -c odoo.conf -u okrmetrics --stop-after-init
```
2. Navigate to the Apps menu inside Odoo, find **Team OKR Tracker**, and click **Install**.
3. Open the **OKRs** App from the top selector:
   - Navigate to **Configuration > Periods** and make a new Period.
   - Go to **Objectives** and create one.
   - Note the **Stars** (Priority) and use the **WYSIWYG editor** (Description).
   - Under Key Results, add a row inline. Give it a start of 0 and target of 10.
   - Finally, expand the Key Result and add a "Check-in" of 5. Watch the progress bar snap to **50%**!

> [!TIP]
> If you have multiple users configured, change their departments. An employee not in that department should technically lose visibility of the OKR item based on our `ir.rule` security configurations!
