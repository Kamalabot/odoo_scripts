# Odoo 18 Business Development & Implementation Roadmap (MSME Focus)

## 1. The Strategy: Odoo 18 vs. Zoho
* **Unified Engine:** Unlike Zoho’s "siloed" apps, Odoo 18 is a single database. Manufacturing, Inventory, and Accounting talk to each other in real-time.
* **Ownership vs. Rental:** Zoho is a "per-user tax." Odoo on a private VPS is a company asset with flat hosting costs regardless of user growth.
* **Industrial Grade:** Odoo’s Shop Floor app is built for tablets and rugged factory use, not just office desks.

---

## 2. Granular Implementation Breakup (Estimates for Indian MSME)

| Phase | Deliverables | Nominal Range |
| :--- | :--- | :--- |
| **Data Sanitation** | Excel cleanup, HSN/GST mapping, Product Variants. | ₹25,000 – ₹45,000 |
| **Core Workflow** | Sales, Purchase, and GST-compliant Accounting. | ₹40,000 – ₹70,000 |
| **Manufacturing (MRP)** | Multi-level BOMs, Work Centers, Shop Floor App. | ₹60,000 – ₹1,20,000 |
| **E-Invoicing/GST** | API Integration for one-click IRN/QR generation. | ₹15,000 – ₹25,000 |
| **Training & Support** | Floor worker training + 1-week Hyper-care. | ₹25,000 – ₹60,000 |
| **Monthly OPEX** | VPS Hosting + Maintenance + Backups. | ₹5,000 – ₹12,000/mo |

---

## 3. Technical Checkpoints: The "Audit" Questions
* **The Version Risk:** "In Excel, if someone deletes a formula, how long until you notice the error?"
* **The Traceability Test:** "Can you trace a customer complaint back to a specific batch of raw material in 3 clicks?"
* **The "Bus Factor":** "If your 'Excel expert' leaves today, can anyone else run the production planning?"

---

## 4. Local-First Implementation (WSL2 / LAN)
For high-speed, internet-independent factory operations, use **Mirrored Networking** to make the WSL instance visible to the office Wi-Fi.

### WSL Configuration (`.wslconfig`)
```ini
[wsl2]
networkingMode=mirrored
firewall=true

New-NetFirewallRule -DisplayName "Odoo 18 LAN Access" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8069

## Incase of db created and login fails

sudo -u odooadmin /opt/odoo/odoo-venv/bin/python /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d teachingserdb -i base,web --stop-after-init

sudo -u postgres psql -d teachingserdb

UPDATE res_users 
SET active = true, password = 'admin' 
WHERE login = 'admin';