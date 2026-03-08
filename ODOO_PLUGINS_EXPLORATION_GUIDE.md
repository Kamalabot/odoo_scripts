# The Comprehensive Guide to Odoo Core Plugins & AI Modules

Odoo's modular architecture allows it to scale from a simple CRM into a full-fledged ERP and beyond. This guide details how to install, explore, and master three advanced plugin categories: **Accounting**, **HR Payroll**, and custom **Apexive LLM (Large Language Model) Modules**.

---

## 🏗️ Part 1: Installing and Managing Plugins

Before deep-diving into specific modules, you must understand how Odoo manages its Ecosystem.

### 1. The Apps Dashboard
Log into Odoo as an Administrator. Navigate to the **Apps** module block.
- **Top Search Bar:** By default, it filters by `Apps`. To see deeper technical plugins (like specific localization packages or sub-modules), remove the `Apps` filter from the search bar. This reveals "Modules".
- **Update Apps List:** If you manually drag a new module folder (like an Apexive LLM plugin) into your Odoo `addons` directory on the server, you *must* click **Update Apps List** in the Apps dashboard before Odoo knows it exists. *(Note: Developer Mode must be active to see this button).*

### 2. Standard vs. Enterprise vs. Custom
- **Standard (Core):** Community modules like basic Sales and Inventory.
- **Enterprise:** Paid modules (like full Accounting & Payroll in newer Odoo versions).
- **Custom (3rd Party):** Modules built by yourself or agencies (like Apexive) that must be manually loaded into your `addons_path`.

---

## 💰 Part 2: Odoo Accounting

Odoo Accounting is arguably the engine's most complex core app. It handles invoicing, ledgers, bank reconciliation, and localized tax reporting.

### 1. Installation & Initialization
- Search for **Accounting** in the Apps menu and click Install.
- **The Chart of Accounts (CoA):** This is the foundation. Odoo usually installs a specific CoA based on your country (Localization).
  - *Where to explore:* **Accounting -> Configuration -> Chart of Accounts**. Look at the structural hierarchy (`Receivables`, `Payables`, `Bank and Cash`, `Income`, `Expenses`).

### 2. Deep Dive: Invoicing & Journal Entries
In Odoo, every financial transaction (Invoices, Bills, Bank Statements) ultimately generates a **Journal Entry** (`account.move`), which contains individual debit/credit **Journal Items** (`account.move.line`).
- *Exploration Exercise:* 
  1. Create a Customer Invoice in the **Accounting -> Customers -> Invoices** menu.
  2. Confirm it.
  3. Click the **Journal Entry** smart button on the invoice. You will see the raw accounting lines (Debit to Account Receivable, Credit to Product Sales, Credit to Taxes).

### 3. Bank Reconciliation
Odoo shines in its reconciliation engine. 
- *Exploration Exercise:* Go to the Accounting Dashboard. Create a new Bank Statement mimicking a customer paying that invoice. Click **Reconcile**. Odoo's engine will try to auto-match the incoming bank line with the open Account Receivable line from your invoice.

### 4. Technical Models to Study
If you are writing scripts to interact with Accounting, study these models:
- `account.move`: The core header for Invoices, Bills, and manual Journal Entries.
- `account.move.line`: The individual debit/credit lines.
- `account.journal`: The "folders" that hold entries (e.g., Sales Journal, Bank Journal, Miscellaneous).
- `account.payment`: The ledger representing money physically moving in/out.

---

## 🧑‍💼 Part 3: HR Payroll

Payroll is highly localized and complex, touching everything from employee attendance to tax withholdings to automatic accounting entries.

### 1. Prerequisites and Installation
To run Payroll, you map out a full HR hierarchy. You must first have the **Employees** app and the **Contracts** app installed.
- Search for **Payroll** (`hr_payroll`) in the Apps menu and Install.

### 2. Deep Dive: The Payroll Pipeline
Odoo Payroll does *not* just pay people; it calculates gross-to-net via a rules engine.
- **Employees (`hr.employee`):** The person receiving the money.
- **Contracts (`hr.contract`):** Defines the base salary, working schedule (e.g., 40h/week), and contract duration. *Payroll cannot run without an Active contract.*
- **Salary Rules (`hr.salary.rule`):** The logic engines. A rule might be "Tax Withholding", which uses Python code to calculate `-15%` of the Gross Salary.
- **Salary Structures (`hr.payroll.structure`):** A collection of Salary Rules grouped together for specific types of employees (e.g., "Standard Salaried Structure" vs "Hourly Contractor Structure").
- **Payslips (`hr.payslip`):** The final document. It takes the Employee, reads the Contract, applies the Structure's Rules, and generates the final math line-by-line.

### 3. Exploration Exercise: Custom Payroll Rules
1. Activate Developer Mode.
2. Go to **Payroll -> Configuration -> Salary Rules**.
3. Create a new Rule named "Bonus".
4. Set the Category to `Basic`.
5. Set the Condition to `Always True`.
6. Set the Computation to `Python Code`.
7. Enter `result = contract.wage * 0.10` (A 10% bonus based on the contract's base wage).
8. Add this rule to your Salary Structure, then generate a Payslip to watch the math execute dynamically!

---

## 🤖 Part 4: Apexive LLM-based Modules

Apexive builds advanced, custom-tailored Odoo modules that integrate Large Language Models (LLMs) deeply into standard ERP workflows. Because these are custom apps, they unlock a completely different way to interact with Odoo.

### 1. Loading Custom Modules
Since Apexive LLM modules are 3rd party, they must be manually placed.
1. Place the module folder (e.g., `apexive_crm_llm`) into your Odoo server's `/mnt/extra-addons/` directory (or wherever your `odoo.conf` defines `addons_path`).
2. Restart the Odoo server service.
3. Turn on Developer Mode, go to **Apps**, click **Update Apps List**.
4. Search for the module and click Install.

### 2. Architectural Concepts of LLM Integration
Apexive modules typically function by hooking into existing Odoo models and using standard API calls to external services (OpenAI, Anthropic, or local LM Studio endpoints).
- **The Prompt Templates:** These modules usually introduce a new model (e.g., `llm.prompt.template`) where administrators can configure the exact system prompts to be sent.
- **Background Cron Jobs:** Because LLM generation can take 10-30 seconds, these modules often don't block the UI. They use Odoo's `ir.cron` or `queue_job` modules to fire requests in the background.

### 3. Exploring 3 Common Apexive LLM Use Cases

**A. CRM Lead Enrichment & Scoring**
- **How it works:** When a new `crm.lead` is created (e.g., via a Website Contact Form), an Apexive automation triggers. It packages the raw notes, email transcript, and company name, and sends it to the LLM.
- **How to explore:** Look for new smart buttons on the CRM Lead form. Check if the module added computed fields like "AI Lead Score (1-100)" or "Suggested Next Action". 
- **Technical hooking:** Look at the module source code for overrides on the `create()` method of `crm.lead` to see how it intercepts the new lead.

**B. Automated Sales Quotation Drafting**
- **How it works:** The LLM reads the history of messages on a Sales Order (`mail.thread`) and automatically drafts a professional email proposing the correct products and quantities.
- **How to explore:** Go to a Sales Order. Look for an "AI Draft Response" button in the Chatter area (the communication thread at the bottom of the page). This button triggers an Odoo Server Action that queries the LLM and drops the drafted text into the chatter input box.

**C. Support Ticket Resolution (Helpdesk)**
- **How it works:** Ingests incoming customer support emails, categorizes them (Billing, Technical, Refund), and generates technical troubleshooting steps by parsing previous solved tickets.
- **How to explore:** Create a mock Helpdesk ticket. The Apexive module should automatically categorize it. Inspect the `ir.actions.server` (Server Actions) in Developer Mode to see the exact python request block firing the API payload over to the LLM provider.

### 4. Advanced Debugging for LLM Modules
If an Apexive module isn't generating responses:
1. **Check the API keys:** Custom modules usually store keys in **Settings -> User/Company settings** or under a dedicated menu block.
2. **Check the Server Logs:** Odoo might be throwing a Timeout error if the LLM provider is slow. Check the terminal where Odoo is running.
3. **Queue Jobs:** If the module uses asynchronous processing, activate Developer mode and inspect the Odoo Scheduled Actions to ensure the background worker isn't deadlocked.
