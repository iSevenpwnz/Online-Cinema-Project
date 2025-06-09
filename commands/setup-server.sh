#!/bin/bash

# Exit the script immediately if any command exits with a non-zero status
set -e

echo "Setting up server for Online Cinema Project deployment..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install Git if not already installed
if ! command -v git &> /dev/null; then
    echo "Installing Git..."
    sudo apt install git -y
fi

# Create project directory
PROJECT_DIR="/home/ubuntu/src/online-cinema-project"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory and cloning repository..."
    mkdir -p /home/ubuntu/src
    cd /home/ubuntu/src
    # Clone repository
    git clone https://github.com/iSevenpwnz/Online-Cinema-Project.git online-cinema-project
    cd online-cinema-project
else
    echo "Project directory already exists."
fi

# Set proper permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/src

echo "Server setup completed successfully!"
echo "You can now run deployment with: bash $PROJECT_DIR/commands/deploy.sh [branch_name]" 