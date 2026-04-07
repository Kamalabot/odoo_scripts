# 1. Install Nginx
sudo apt-get install nginx -y

# 2. Tell Odoo it is behind a proxy (update odoo.conf)
sudo sed -i 's/proxy_mode = False/proxy_mode = True/g' /opt/odoo/odoo.conf
sudo systemctl restart odoo

# 3. Create the Nginx routing configuration
sudo tee /etc/nginx/sites-available/odoo > /dev/null <<EOF
upstream odoo {
    server 127.0.0.1:8069;
}

server {
    listen 80;
    server_name localhost;

    # Common Proxy Headers
    proxy_set_header X-Forwarded-Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header X-Real-IP \$remote_addr;

    # Standard HTTP Traffic
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    # WebSocket Traffic (The Fix)
    location /websocket {
        proxy_pass http://odoo;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

# 4. Enable the configuration and restart Nginx
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/odoo || true
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
