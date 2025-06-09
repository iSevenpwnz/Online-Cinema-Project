#!/bin/bash

# Exit the script immediately if any command exits with a non-zero status
set -e

# Function to handle errors with custom messages
handle_error() {
    echo "Error: $1"
    exit 1
}

# Get the target branch from the first argument, default to 'develop' if not provided
TARGET_BRANCH=${1:-develop}
echo "Deploying branch: $TARGET_BRANCH"

# Navigate to the application directory
PROJECT_DIR="/home/ubuntu/src/online-cinema-project"
echo "Project directory: $PROJECT_DIR"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Project directory does not exist. Running initial setup..."
    mkdir -p /home/ubuntu/src
    cd /home/ubuntu/src
    git clone https://github.com/iSevenpwnz/Online-Cinema-Project.git online-cinema-project
    cd "$PROJECT_DIR"
else
    cd "$PROJECT_DIR" || handle_error "Failed to navigate to $PROJECT_DIR"
fi

echo "Current directory: $(pwd)"
echo "Current git status:"
git status --short || echo "Git status failed"
echo "Current branch: $(git branch --show-current)"

# Fetch the latest changes from the remote repository
echo "Fetching the latest changes from the remote repository..."
git fetch origin $TARGET_BRANCH || handle_error "Failed to fetch updates from the 'origin' remote for branch '$TARGET_BRANCH'."

# Reset the local repository to match the remote target branch
echo "Resetting the local repository to match 'origin/$TARGET_BRANCH'..."
git reset --hard origin/$TARGET_BRANCH || handle_error "Failed to reset the local repository to 'origin/$TARGET_BRANCH'."

echo "After reset - current branch: $(git branch --show-current)"
echo "After reset - last commit: $(git log -1 --oneline)"

# (Optional) Pull any new tags from the remote repository
echo "Fetching tags from the remote repository..."
git fetch origin --tags || handle_error "Failed to fetch tags from the 'origin' remote."

# Check if docker-compose-prod.yml exists
if [ ! -f "docker-compose-prod.yml" ]; then
    echo "Warning: docker-compose-prod.yml not found in current directory"
    echo "Available files:"
    ls -la | grep -E "(docker-compose|yml|yaml)" || echo "No docker-compose files found"
    handle_error "docker-compose-prod.yml file not found"
fi

# Build and run Docker containers with Docker Compose v2
echo "Building and starting Docker containers..."
docker compose -f docker-compose-prod.yml up -d --build || handle_error "Failed to build and run Docker containers using docker-compose-prod.yml."

# Print a success message upon successful deployment
echo "Deployment of branch '$TARGET_BRANCH' completed successfully."