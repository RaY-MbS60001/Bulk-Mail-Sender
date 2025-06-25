# deployment/setup.sh
#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3-pip python3-dev nginx

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install gunicorn gevent

# Setup nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/bulk_email_app
sudo ln -s /etc/nginx/sites-available/bulk_email_app /etc/nginx/sites-enabled
sudo systemctl restart nginx

# Setup systemd service
sudo cp deployment/bulk_email_app.service /etc/systemd/system/
sudo systemctl start bulk_email_app
sudo systemctl enable bulk_email_app