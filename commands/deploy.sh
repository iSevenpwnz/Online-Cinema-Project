#!/bin/bash

# Exit the script immediately if any command exits with a non-zero status
set -e

# Function to handle errors with custom messages
handle_error() {
    echo "Error: $1"
    cleanup
    exit 1
}

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    rm -f "$LOCK_FILE"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Deployment lock to prevent concurrent deployments
LOCK_FILE="/tmp/cinema-deploy.lock"
LOCK_TIMEOUT=300  # 5 minutes

echo "=== Online Cinema Deployment Started ==="
echo "Timestamp: $(date)"

# Check for existing deployment
if [ -f "$LOCK_FILE" ]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    echo "Lock file exists (PID: $LOCK_PID). Checking if process is still running..."
    
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        echo "Another deployment is already in progress (PID: $LOCK_PID)"
        echo "Waiting for it to complete (timeout: ${LOCK_TIMEOUT}s)..."
        
        WAIT_TIME=0
        while [ -f "$LOCK_FILE" ] && [ $WAIT_TIME -lt $LOCK_TIMEOUT ]; do
            sleep 10
            WAIT_TIME=$((WAIT_TIME + 10))
            echo "Waiting... ${WAIT_TIME}s/${LOCK_TIMEOUT}s"
        done
        
        if [ -f "$LOCK_FILE" ]; then
            echo "Timeout waiting for previous deployment. Removing stale lock."
            rm -f "$LOCK_FILE"
        fi
    else
        echo "Lock file exists but process is not running. Removing stale lock."
        rm -f "$LOCK_FILE"
    fi
fi

# Create deployment lock
echo $$ > "$LOCK_FILE"
echo "Deployment lock created (PID: $$)"

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

# Stop existing containers gracefully
echo "Stopping existing containers..."
docker compose -f docker-compose-prod.yml down --timeout 30 || echo "No containers to stop or some containers failed to stop"

# Clean up unused Docker resources to free space
echo "Cleaning up Docker resources..."
docker system prune -f --volumes || echo "Docker cleanup completed with warnings"

# Build and run Docker containers with optimizations
echo "Building and starting Docker containers..."
echo "This may take several minutes..."

# Build with no cache for clean deployment and parallel builds
DOCKER_BUILDKIT=1 docker compose -f docker-compose-prod.yml build --no-cache --parallel || handle_error "Failed to build Docker containers"

# Start containers with timeout
timeout 600 docker compose -f docker-compose-prod.yml up -d || handle_error "Failed to start Docker containers (timeout: 10 minutes)"

# Wait for containers to be healthy
echo "Waiting for containers to be ready..."
sleep 10

# Check if containers are running
echo "Checking container status..."
docker compose -f docker-compose-prod.yml ps

# Verify main application is responding (if health check exists)
echo "Verifying deployment..."
MAIN_CONTAINER=$(docker compose -f docker-compose-prod.yml ps --services | head -1)
if [ -n "$MAIN_CONTAINER" ]; then
    echo "Main container: $MAIN_CONTAINER"
    docker compose -f docker-compose-prod.yml logs --tail 20 "$MAIN_CONTAINER" || echo "Could not fetch logs"
fi

# Print a success message upon successful deployment
echo "=== Deployment Summary ==="
echo "Branch: $TARGET_BRANCH"
echo "Completed at: $(date)"
echo "Running containers:"
docker compose -f docker-compose-prod.yml ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
echo "=== Deployment of branch '$TARGET_BRANCH' completed successfully! ==="