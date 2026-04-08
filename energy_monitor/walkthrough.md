# Energy Monitor Addon Implementation Walkthrough

I have successfully created the `energy_monitor` Odoo addon as per the design document.

## What was built:

1. **Models:**
   - `energy.meter`: Represents physical utility meters with fields like utility type, rate, and budget.
   - `energy.reading`: Represents monthly readings, computing consumption based on the previous reading and cost based on the meter's configuration.
   - `res.config.settings`: Inherits base config to allow global settings for default electricity rates and alert emails.

2. **Views & Menus:**
   - Under the top-level **Facility** menu, you'll find the **Energy Management** application.
   - **Meters and Readings** have rich Kanban/Tree/Form views.
   - Reading views include **Pivot** and **Graph** configurations that allow slicing data by month, meter, and department out-of-the-box.

3. **Automation & Chatter:**
   - Added Odoo's Chatter (`mail.thread`) to both models for full logging and messaging tracking.
   - Created a strict **Automated Action** (`base.automation` + Server Action) that detects if a reading cost exceeds the monthly budget, automatically posting a warning Activity for the department manager.

4. **Security Groups:**
   - **Energy Management / User**: Basic users who can read meters and draft new readings.
   - **Energy Management / Manager**: Administrative users who can create meters, change utility rates, and resolve readings.

## How to use the Security Groups in Odoo GUI:

> [!TIP]
> Assigning users to the Energy Monitor groups is done through the standard Odoo Settings interface.

1. Turn on **Developer Mode** (Settings -> General Settings -> scroll down and click "Activate the developer mode").
2. Navigate to **Settings -> Users & Companies -> Users**.
3. Select any user you'd like to configure.
4. Under the **Access Rights** tab, look for the section titled **Energy Management**.
5. You will see a dropdown field where you can select:
   - *Blank* (No explicit access)
   - *User* (`group_energy_user`)
   - *Manager* (`group_energy_manager`)
6. Ensure your main testing user is set to `Manager` to have full access to create meters.

You can now restart your Odoo service and update your module list to install the `energy_monitor` add-on!
