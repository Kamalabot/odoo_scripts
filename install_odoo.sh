#!/bin/bash
# =========================================================================
# Odoo 18 Bare-Metal Installer for WSL (Ubuntu 22.04)
# Optimized for Air-Gap Portability & GPU Server Deployment
# =========================================================================
set -e

echo "🚀 Starting Master Odoo 18 Installation..."

# 1. System-Level Dependencies & WSL Patch
echo "📦 Installing C-libraries and System Headers..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git python3 python3-pip python3-venv python3-dev \
    build-essential libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
    nodejs npm libpq-dev wkhtmltopdf postgresql postgresql-client \
    libevent-dev libffi-dev

# Fix the WSL systemd timeout bug
echo "🛠️ Applying WSL Systemd Network Patch..."
sudo systemctl disable systemd-networkd-wait-online.service || true

# 2. Database Configuration
echo "🗄️ Configuring PostgreSQL..."
sudo service postgresql start
# Create user 'odoo' and set password to 'odoo' for TCP/IP access
sudo su - postgres -c "psql -c \"CREATE USER odoo WITH PASSWORD 'odoo' SUPERUSER;\"" || \
sudo su - postgres -c "psql -c \"ALTER USER odoo WITH PASSWORD 'odoo' SUPERUSER;\""

# 3. Directory & Source Code
echo "📥 Setting up Odoo Source..."
sudo mkdir -p /opt/odoo
sudo chown -R $USER:$USER /opt/odoo
if [ -d "/opt/odoo/.git" ]; then
    cd /opt/odoo && git pull
else
    git clone https://www.github.com/odoo/odoo --depth 1 --branch 18.0 /opt/odoo
fi

# 4. Python Virtual Environment & Dependency Battle-Plan
echo "🐍 Building Python Environment..."
cd /opt/odoo
python3 -m venv odoo-venv
source odoo-venv/bin/activate

# Step A: Upgrade base tools
pip install --upgrade pip wheel setuptools_scm[toml]

# Step B: The "Cython Massacre" & "Setuptools 70" Fixes
pip install "setuptools<70.0.0"
pip install "Cython<3.0" greenlet

# Step C: The Gevent/Cbor2 Binary Strategy (Bypassing compiler traps)
echo "⚙️  Compiling Stubborn Dependencies..."
pip install cbor2==5.4.2 --no-build-isolation
pip install --only-binary gevent gevent==21.8.0

# Step D: Final Requirements Sweep
echo "📚 Installing remaining Odoo requirements..."
pip install -r requirements.txt

echo "========================================================"
echo "✅ TOTAL SUCCESS: Odoo 18 is now a weapon in your hands."
echo "========================================================"
echo "🔥 IGNITION COMMAND:"
echo "cd /opt/odoo && source odoo-venv/bin/activate"
echo "./odoo-bin -r odoo -w odoo --db_host=localhost --addons-path=addons"
echo "========================================================"
