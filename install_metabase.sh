# 1. Install Java 17 Headless (No GUI bloat)
sudo apt update -y
sudo apt install -y openjdk-17-jre-headless

# 2. Create the production directory in /opt
sudo mkdir -p /opt/metabase
cd /opt/metabase

# 3. Download the latest Open-Source Metabase JAR
sudo wget https://downloads.metabase.com/latest/metabase.jar -O /opt/metabase/metabase.jar

# 4. Create a dedicated, unprivileged system user for security
sudo useradd -r -s /bin/false metabase
sudo chown -R metabase:metabase /opt/metabase

# 5. Create the systemd service file
sudo bash -c 'cat << EOF > /etc/systemd/system/metabase.service
[Unit]
Description=Metabase server
After=syslog.target
After=network.target

[Service]
WorkingDirectory=/opt/metabase/
ExecStart=/usr/bin/java -jar /opt/metabase/metabase.jar
User=metabase
Type=simple
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=metabase
SuccessExitStatus=143

[Install]
WantedBy=multi-user.target
EOF'

# 6. Reload the systemd daemon, enable on boot, and start the engine
sudo systemctl daemon-reload
sudo systemctl enable metabase.service
sudo systemctl start metabase.service
