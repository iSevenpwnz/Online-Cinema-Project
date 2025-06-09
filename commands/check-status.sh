#!/bin/bash

echo "=== Online Cinema Project Deployment Status ==="
echo ""

# Check current directory
echo "Current directory: $(pwd)"
echo ""

# Check current git branch and status
if [ -d ".git" ]; then
    echo "=== Git Status ==="
    echo "Current branch: $(git branch --show-current)"
    echo "Last commit: $(git log -1 --oneline)"
    echo "Remote tracking: $(git branch -vv | grep \* | awk '{print $4}' | sed 's/\[//g' | sed 's/\]//g')"
    echo ""
fi

# Check Docker containers status
echo "=== Docker Status ==="
if command -v docker &> /dev/null; then
    echo "Docker containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    echo "Docker images (online-cinema related):"
    docker images | grep -E "(online-cinema|cinema)" || echo "No cinema-related images found"
    echo ""
else
    echo "Docker is not installed or not available"
    echo ""
fi

# Check Docker Compose status
echo "=== Docker Compose Status ==="
if [ -f "docker-compose-prod.yml" ]; then
    docker compose -f docker-compose-prod.yml ps
else
    echo "docker-compose-prod.yml not found"
fi
echo ""

# Check system resources
echo "=== System Resources ==="
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h | grep -E "(Filesystem|/dev/)"
echo ""

# Check application logs (last 10 lines)
echo "=== Recent Application Logs ==="
if command -v docker &> /dev/null; then
    MAIN_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(app|web|cinema)" | head -1)
    if [ ! -z "$MAIN_CONTAINER" ]; then
        echo "Last 10 lines from $MAIN_CONTAINER:"
        docker logs --tail 10 $MAIN_CONTAINER
    else
        echo "No main application container found"
    fi
else
    echo "Docker not available for log checking"
fi

echo ""
echo "=== Status Check Complete ===" 