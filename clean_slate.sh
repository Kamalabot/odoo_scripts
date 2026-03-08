#!/bin/bash

# --- CONFIGURATION ---
SOURCE_DB="ai_pf_db"          # The DB with demo data
TARGET_DB="ai_pf_db_clean"    # The new clean production DB
CONFIG="/etc/odoo/odoo.conf"
ODOO_BIN="/opt/odoo/odoo-bin"
PYTHON_PATH="/opt/odoo/odoo-venv/bin/python3"

echo "-----------------------------------------------"
echo "PHASE 1: Extracting Blueprint from $SOURCE_DB"
echo "-----------------------------------------------"

# Use your SQL logic to get the comma-separated list
# We exclude 'base' and 'web' because Odoo installs those by default
INSTALLED_APPS=$(cd /tmp && sudo -u postgres psql -d $SOURCE_DB -U postgres -t -A -c "SELECT name FROM ir_module_module WHERE state = 'installed' AND name NOT LIKE 'base%' AND name NOT LIKE 'web%';" | paste -sd "," -)

if [ -z "$INSTALLED_APPS" ]; then
    echo "Error: No installed apps found or Source DB does not exist."
    exit 1
fi

echo "Blueprint found: $INSTALLED_APPS"

echo "-----------------------------------------------"
echo "PHASE 2: Cleaning the Slate"
echo "-----------------------------------------------"

# Stop Odoo to release locks
sudo systemctl stop odoo

# Drop target DB if it already exists from a previous practice run
sudo -u odoo dropdb $TARGET_DB --if-exists

echo "-----------------------------------------------"
echo "PHASE 3: Initializing $TARGET_DB (No Demo Data)"
echo "-----------------------------------------------"

# The Heavy Lifting
$PYTHON_PATH $ODOO_BIN -c $CONFIG \
    -d $TARGET_DB \
    -i $INSTALLED_APPS \
    --without-demo=all \
    --stop-after-init

echo "-----------------------------------------------"
echo "SUCCESS: $TARGET_DB is ready for production."
echo "-----------------------------------------------"

# Optional: Restart the service pointing to the new DB
# sudo systemctl start odoo
