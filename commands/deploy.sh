#!/bin/bash

set -e

handle_error() {
    echo "Error: $1"
    exit 1
}

BRANCH="${DEPLOY_BRANCH:-cd-settings}"

cd /home/ubuntu/src/online-cinema-project || handle_error "Failed to navigate to the application directory."

echo "Fetching the latest changes from the remote repository..."
git fetch origin $BRANCH || handle_error "Failed to fetch updates from the 'origin' remote."

echo "Resetting the local repository to match 'origin/$BRANCH'..."
git reset --hard origin/$BRANCH || handle_error "Failed to reset the local repository to 'origin/$BRANCH'."

echo "Fetching tags from the remote repository..."
git fetch origin --tags || handle_error "Failed to fetch tags from the 'origin' remote."

docker compose -f docker-compose-prod.yml up -d --build || handle_error "Failed to build and run Docker containers using docker-compose-prod.yml."

echo "Deployment completed successfully."
