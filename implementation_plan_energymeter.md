# Smart Energy & Utility Monitor (`energy_monitor`)

We are building a new Odoo addon, `energy_monitor`, to track utility consumption and costs per department, using advanced Odoo concepts like monetary fields, mail threads (chatter), pivot/graph views, automated actions, and global settings.

## User Review Required

> [!IMPORTANT]
> - Do you want to add a specific Top-Level Menu (e.g., "Energy Management") or should this be placed under an existing menu (like "Facility" if it exists, or just standalone)?
> - For the Automated Action email alert, do we want a specific email template or a simple text notification when `cost > monthly_budget`?
> - Let me know if there are any specific user groups needed (like `group_energy_user`, `group_energy_manager`) or if basic Odoo internal user groups (`base.group_user`) are sufficient for now. I will create a basic 'Energy Manager' and 'Energy User' group.

## Proposed Changes

We will create a new directory `d:\gitFolders\odoo_scripts\energy_monitor` with the following structure:

### 1. Module Initialization
#### [NEW] [__manifest__.py](file:///d:/gitFolders/odoo_scripts/energy_monitor/__manifest__.py)
Defines the addon metadata, dependencies (`base`, `mail`, `base_automation`, `hr`), and the list of data/view XML files.
#### [NEW] [__init__.py](file:///d:/gitFolders/odoo_scripts/energy_monitor/__init__.py)
Imports the `models` directory.

---
### 2. Python Models
#### [NEW] [models/__init__.py](file:///d:/gitFolders/odoo_scripts/energy_monitor/models/__init__.py)
Imports all model files.
#### [NEW] [models/energy_meter.py](file:///d:/gitFolders/odoo_scripts/energy_monitor/models/energy_meter.py)
Defines `energy.meter` model.
- Includes fields: `name`, `ref`, `utility_type`, `unit`, `department_id`, `location`, `rate`, `currency_id`, `monthly_budget`, `active`.
- Uses `mail.thread` and `mail.activity.mixin` for chatter support.
#### [NEW] [models/energy_reading.py](file:///d:/gitFolders/odoo_scripts/energy_monitor/models/energy_reading.py)
Defines `energy.reading` model.
- Includes fields: `meter_id`, `reading_date`, `meter_value`, `previous_value` (computed), `consumption` (computed, store=True), `cost` (computed, store=True), `notes`, `month` (computed), `state`.
#### [NEW] [models/res_config_settings.py](file:///d:/gitFolders/odoo_scripts/energy_monitor/models/res_config_settings.py)
Extends `res.config.settings` to add global settings like `energy_alert_email` and `default_rate_electricity` via `ir.config_parameter`.

---
### 3. Views and Menus
#### [NEW] [views/energy_meter_views.xml](file:///d:/gitFolders/odoo_scripts/energy_monitor/views/energy_meter_views.xml)
Defines `tree` and `form` views for `energy.meter`. Form view will include the `oe_chatter` section.
#### [NEW] [views/energy_reading_views.xml](file:///d:/gitFolders/odoo_scripts/energy_monitor/views/energy_reading_views.xml)
Defines `tree`, `form`, `graph` (bar/line/pie), and `pivot` views for `energy.reading`. Graph and Pivot views will allow deep analysis of consumption and cost by month, utility type, and department.
#### [NEW] [views/res_config_settings_views.xml](file:///d:/gitFolders/odoo_scripts/energy_monitor/views/res_config_settings_views.xml)
Provides the UI in the Settings module to configure the app-wide parameters.
#### [NEW] [views/energy_menus.xml](file:///d:/gitFolders/odoo_scripts/energy_monitor/views/energy_menus.xml)
Defines the main `Energy` application menu and submenus to navigate meters, readings, and settings.

---
### 4. Data and Automation
#### [NEW] [data/energy_automation.xml](file:///d:/gitFolders/odoo_scripts/energy_monitor/data/energy_automation.xml)
Creates a `base.automation` record that triggers an email or activity when a reading's `cost` exceeds the meter's `monthly_budget`.

---
### 5. Security
#### [NEW] [security/energy_security.xml](file:///d:/gitFolders/odoo_scripts/energy_monitor/security/energy_security.xml)
Defines security categories and groups (User/Manager) for the module.
#### [NEW] [security/ir.model.access.csv](file:///d:/gitFolders/odoo_scripts/energy_monitor/security/ir.model.access.csv)
Grants access rules for the groups on `energy.meter` and `energy.reading`.

## Open Questions

- What should be the default state flow for `energy.reading`? (e.g., `draft` -> `confirmed`)
- For the `cost > monthly_budget` rule, does Odoo in this environment have outgoing email servers set up, or should we just trigger a `mail.activity` instead for testing?

## Verification Plan

### Automated Tests
- No automated tests required for now, but we will ensure syntax and references via XML/Python validation (e.g., building Odoo module locally or with a standard linter if available).

### Manual Verification
- Install the `energy_monitor` module.
- Navigate to the newly created Energy interface.
- Add an `energy.meter` and a few related `energy.reading` records to verify model interconnections and computations.
- Check graph and pivot views to see aggregated cost/consumption.
- Verify settings form is working and global parameters are saving.
- Test the reading record form to ensure chatter functionality is correctly attached.
