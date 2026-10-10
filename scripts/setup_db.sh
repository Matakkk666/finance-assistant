#!/bin/bash
apt-get update
apt-get install -y postgresql
sudo -u postgres psql -c "CREATE USER \"user\" WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE finance_db OWNER \"user\";"
cd /root/finance-assistant
source venv/bin/activate
alembic upgrade head
