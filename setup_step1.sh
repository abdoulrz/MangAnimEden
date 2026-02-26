#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== ManganimEden Contabo Migration: Step 1 ==="
echo "Updating packages..."
apt update && apt upgrade -y

echo "Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo "Installing dependencies..."
apt install python3-pip python3-venv nginx postgresql postgresql-contrib libpq-dev curl git -y

echo "=== Step 1 complete! ==="
