#!/bin/bash
# =========================================================================
# Odoo 18 Automated Bare-Metal Installer & Service Manager (WSL/Ubuntu)
# =========================================================================
set -e

# Capture current user to assign ownership
RUNNER=$USER
ODOO_HOME="/opt/odoo"

echo "🚀 Starting Master Odoo 18 Installation & Deployment..."

# 1. System-Level Dependencies
echo "📦 Installing C-libraries and System Headers..."
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv python3-dev \
    build-essential libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
    nodejs npm libpq-dev wkhtmltopdf postgresql postgresql-client \
    libevent-dev libffi-dev

# Apply WSL systemd network patch
echo "🛠️ Applying WSL Systemd Patch..."
sudo systemctl disable systemd-networkd-wait-online.service || true

# 2. Database Configuration & Rescue
echo "🗄️ Cleaning WSL PostgreSQL Locks and Configuring..."
sudo pkill -u postgres || true
sudo rm -f /var/lib/postgresql/14/main/postmaster.pid
sudo rm -f /var/run/postgresql/*.pid

# Force start the cluster
sudo pg_ctlcluster 14 main start || sudo service postgresql start

# The "Magical" pg_hba.conf Patch
echo "🔓 Patching PostgreSQL Authentication..."
sudo sed -i 's/peer/trust/g' /etc/postgresql/14/main/pg_hba.conf
sudo sed -i 's/scram-sha-256/trust/g' /etc/postgresql/14/main/pg_hba.conf
sudo service postgresql restart

# Create the DB User
sudo su - postgres -c "psql -c \"CREATE USER odoo WITH PASSWORD 'odoo' SUPERUSER;\"" || \
sudo su - postgres -c "psql -c \"ALTER USER odoo WITH PASSWORD 'odoo' SUPERUSER;\""

# 3. Directory & Source Code
echo "📥 Setting up Odoo Source..."
sudo mkdir -p $ODOO_HOME
sudo chown -R $RUNNER:$RUNNER $ODOO_HOME
if [ -d "$ODOO_HOME/.git" ]; then
    cd $ODOO_HOME && git pull
else
    git clone https://www.github.com/odoo/odoo --depth 1 --branch 18.0 $ODOO_HOME
fi

# 4. Patching Odoo Source Code (GeoIP Bug)
echo "🩹 Patching Odoo GeoIP Bug..."
cd $ODOO_HOME
sudo sed -i '/maxminddb = None/a \ \nclass GeoIPPlaceholder:\n    def __getattr__(self, name): return False\n    def __getitem__(self, name): return False\n    def __bool__(self): return False\n\nGEOIP_EMPTY_COUNTRY = GeoIPPlaceholder()\nGEOIP_EMPTY_CITY = GeoIPPlaceholder()' odoo/http.py || true

# 5. Python Virtual Environment & Modernized Dependencies
echo "🐍 Building Python Environment..."
python3 -m venv odoo-venv
source odoo-venv/bin/activate

pip install --upgrade pip wheel setuptools
echo "⚙️ Installing Modernized C-Extensions..."
pip install "greenlet>=2.0.0" "gevent>=22.10.2" "cbor2>=5.4.3"
pip install rjsmin cssmin lxml_html_clean babel passlib werkzeug psycopg2-binary

echo "📚 Installing remaining requirements..."
sed -i 's/cbor2==/cbor2>=/g' requirements.txt
sed -i 's/greenlet==/greenlet>=/g' requirements.txt
sed -i 's/gevent==/gevent>=/g' requirements.txt
pip install -r requirements.txt

# 6. Generate Dedicated Configuration File
echo "📝 Generating odoo.conf..."
cat <<EOF > $ODOO_HOME/odoo.conf
[options]
admin_passwd = admindb
db_host = 127.0.0.1
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = addons,odoo/addons
proxy_mode = False
limit_time_cpu = 600
limit_time_real = 1200
EOF

# Ensure the runner owns the conf file so Odoo can encrypt the admin_passwd
sudo chown $RUNNER:$RUNNER $ODOO_HOME/odoo.conf

# 7. Create and Start the Systemd Service
echo "⚙️ Creating Odoo systemd service..."
sudo tee /etc/systemd/system/odoo.service > /dev/null <<EOF
[Unit]
Description=Odoo 18 Server
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo
PermissionsStartOnly=true
User=$RUNNER
Group=$RUNNER
WorkingDirectory=$ODOO_HOME
ExecStart=$ODOO_HOME/odoo-venv/bin/python3 $ODOO_HOME/odoo-bin -c $ODOO_HOME/odoo.conf
StandardOutput=journal+console
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "🚀 Enabling and starting Odoo service..."
sudo systemctl enable odoo
sudo systemctl restart odoo

echo "========================================================"
echo "✅ TOTAL SUCCESS: Odoo 18 is deployed and running."
echo "========================================================"
echo "🌐 Access the UI at: http://localhost:8069"
echo "📜 View live logs: sudo journalctl -u odoo -f"
echo "========================================================"
