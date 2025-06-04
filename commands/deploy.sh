#!/bin/bash

# Exit the script immediately if any command exits with a non-zero status
set -e

# Prints a custom error message and exits the script with status 1.
#
# Arguments:
#
# * Error message to display before exiting.
#
# Outputs:
#
# * Prints the provided error message to STDOUT.
#
# Returns:
#
# * Exits the script with status code 1.
#
# Example:
#
# ```bash
# handle_error "Failed to connect to database"
# ```
handle_error() {
    echo "Error: $1"
    exit 1
}

# Navigate to the application directory
cd /home/ubuntu/src/mate-fastapi-homework-5 || handle_error "Failed to navigate to the application directory."

# Fetch the latest changes from the remote repository
echo "Fetching the latest changes from the remote repository..."
git fetch origin main || handle_error "Failed to fetch updates from the 'origin' remote."

# Reset the local repository to match the remote 'main' branch
echo "Resetting the local repository to match 'origin/main'..."
git reset --hard origin/main || handle_error "Failed to reset the local repository to 'origin/main'."

# (Optional) Pull any new tags from the remote repository
echo "Fetching tags from the remote repository..."
git fetch origin --tags || handle_error "Failed to fetch tags from the 'origin' remote."

# Build and run Docker containers with Docker Compose v2
docker compose -f docker-compose-prod.yml up -d --build || handle_error "Failed to build and run Docker containers using docker-compose-prod.yml."

# Print a success message upon successful deployment
echo "Deployment completed successfully."
