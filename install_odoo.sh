#!/bin/bash
# =========================================================================
# Odoo 18 Automated Bare-Metal Installer for WSL (Ubuntu)
# =========================================================================
set -e

echo "🚀 Starting Master Odoo 18 Installation..."

# 1. System-Level Dependencies
echo "📦 Installing C-libraries and System Headers..."
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv python3-dev \
    build-essential libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
    nodejs npm libpq-dev wkhtmltopdf postgresql postgresql-client \
    libevent-dev libffi-dev

# Apply WSL systemd timeout patch
echo "🛠️ Applying WSL Systemd Network Patch..."
sudo systemctl disable systemd-networkd-wait-online.service || true

# 2. Database Configuration & Rescue
echo "🗄️ Cleaning WSL PostgreSQL Locks and Configuring..."
sudo pkill -u postgres || true
sudo rm -f /var/lib/postgresql/14/main/postmaster.pid
sudo rm -f /var/run/postgresql/*.pid

# Force start the cluster
sudo pg_ctlcluster 14 main start || sudo service postgresql start

# The "Magical" pg_hba.conf Patch: Bypass strict peer/scram checks for local dev
echo "🔓 Patching PostgreSQL Authentication..."
sudo sed -i 's/peer/trust/g' /etc/postgresql/14/main/pg_hba.conf
sudo sed -i 's/scram-sha-256/trust/g' /etc/postgresql/14/main/pg_hba.conf
sudo service postgresql restart

# Create the DB User
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

# 4. Patching Odoo Source Code (GeoIP Bug)
echo "🩹 Patching Odoo GeoIP Bug..."
cd /opt/odoo
sudo sed -i '/maxminddb = None/a \ \nclass GeoIPPlaceholder:\n    def __getattr__(self, name): return False\n    def __getitem__(self, name): return False\n    def __bool__(self): return False\n\nGEOIP_EMPTY_COUNTRY = GeoIPPlaceholder()\nGEOIP_EMPTY_CITY = GeoIPPlaceholder()' odoo/http.py || true

# 5. Python Virtual Environment & Modernized Dependencies
echo "🐍 Building Python Environment..."
python3 -m venv odoo-venv
source odoo-venv/bin/activate

# Step A: Upgrade core installers
pip install --upgrade pip wheel setuptools

# Step B: Pre-install the "Crashers" with modern versions
echo "⚙️  Installing Modernized C-Extensions..."
pip install "greenlet>=2.0.0" "gevent>=22.10.2" "cbor2>=5.4.3"

# Step C: Install the hidden front-end bundlers and core libraries
pip install rjsmin cssmin lxml_html_clean babel passlib werkzeug psycopg2-binary

# Step D: Unpin the conflict dependencies in the requirements file and install the rest
echo "📚 Installing remaining Odoo requirements..."
sed -i 's/cbor2==/cbor2>=/g' requirements.txt
sed -i 's/greenlet==/greenlet>=/g' requirements.txt
sed -i 's/gevent==/gevent>=/g' requirements.txt
pip install -r requirements.txt

# 6. Generate Dedicated Configuration File
echo "📝 Generating odoo.conf..."
cat <<EOF > odoo.conf
[options]
admin_passwd = admin
db_host = 127.0.0.1
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = addons,odoo/addons
proxy_mode = False
limit_time_cpu = 600
limit_time_real = 1200
EOF

echo "========================================================"
echo "✅ TOTAL SUCCESS: Odoo 18 installation complete."
echo "========================================================"
echo "🔥 IGNITION COMMAND:"
echo "cd /opt/odoo && source odoo-venv/bin/activate"
echo "python3 odoo-bin -c odoo.conf -d test_db -i base"
echo "========================================================"
