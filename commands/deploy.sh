#!/bin/bash

# Exit the script immediately if any command exits with a non-zero status
set -e

# Function to handle errors with custom messages
handle_error() {
    echo "Error: $1"
    exit 1
}

# Get the target branch from the first argument, default to 'main' if not provided
TARGET_BRANCH=${1:-main}
echo "Deploying branch: $TARGET_BRANCH"

# Navigate to the application directory
cd /home/ubuntu/src/online-cinema-project || handle_error "Failed to navigate to the application directory."

# Fetch the latest changes from the remote repository
echo "Fetching the latest changes from the remote repository..."
git fetch origin $TARGET_BRANCH || handle_error "Failed to fetch updates from the 'origin' remote for branch '$TARGET_BRANCH'."

# Reset the local repository to match the remote target branch
echo "Resetting the local repository to match 'origin/$TARGET_BRANCH'..."
git reset --hard origin/$TARGET_BRANCH || handle_error "Failed to reset the local repository to 'origin/$TARGET_BRANCH'."

# (Optional) Pull any new tags from the remote repository
echo "Fetching tags from the remote repository..."
git fetch origin --tags || handle_error "Failed to fetch tags from the 'origin' remote."

# Build and run Docker containers with Docker Compose v2
echo "Building and starting Docker containers..."
docker compose -f docker-compose-prod.yml up -d --build || handle_error "Failed to build and run Docker containers using docker-compose-prod.yml."

# Print a success message upon successful deployment
echo "Deployment of branch '$TARGET_BRANCH' completed successfully."