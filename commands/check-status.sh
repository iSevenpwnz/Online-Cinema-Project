#!/bin/bash

echo "=== Online Cinema Project Deployment Status ==="
echo "Timestamp: $(date)"
echo ""

# Check current directory
echo "Current directory: $(pwd)"
echo ""

# Check if deployment lock exists
LOCK_FILE="/tmp/cinema-deploy.lock"
if [ -f "$LOCK_FILE" ]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "unknown")
    echo "🔒 DEPLOYMENT LOCK ACTIVE (PID: $LOCK_PID)"
    if [ -n "$LOCK_PID" ] && [ "$LOCK_PID" != "unknown" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        echo "   ✅ Lock process is running"
    else
        echo "   ⚠️  Lock file exists but process not found (stale lock)"
    fi
    echo ""
else
    echo "🔓 No deployment lock found"
    echo ""
fi

# Check current git branch and status
if [ -d ".git" ]; then
    echo "=== Git Status ==="
    echo "Current branch: $(git branch --show-current)"
    echo "Last commit: $(git log -1 --oneline)"
    echo "Remote tracking: $(git branch -vv | grep \* | awk '{print $4}' | sed 's/\[//g' | sed 's/\]//g' 2>/dev/null || echo 'No tracking info')"
    echo "Git status:"
    git status --porcelain || echo "Git status failed"
    echo ""
fi

# Check Docker daemon status
echo "=== Docker Status ==="
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo "✅ Docker daemon is running"
    else
        echo "❌ Docker daemon is not responding"
    fi
    
    echo ""
    echo "Docker containers (all):"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.CreatedAt}}" 2>/dev/null || echo "Failed to list containers"
    echo ""
    
    echo "Docker images (cinema related):"
    docker images | grep -E "(online-cinema|cinema|theater)" || echo "No cinema-related images found"
    echo ""
else
    echo "❌ Docker is not installed or not available"
    echo ""
fi

# Check Docker Compose status for production
echo "=== Docker Compose Status (Production) ==="
if [ -f "docker-compose-prod.yml" ]; then
    echo "Production services status:"
    docker compose -f docker-compose-prod.yml ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Failed to get compose status"
    echo ""
    
    # Check service health
    echo "Service health check:"
    SERVICES=$(docker compose -f docker-compose-prod.yml ps --services 2>/dev/null || echo "")
    if [ -n "$SERVICES" ]; then
        for service in $SERVICES; do
            CONTAINER_STATUS=$(docker compose -f docker-compose-prod.yml ps "$service" --format "{{.Status}}" 2>/dev/null || echo "unknown")
            if echo "$CONTAINER_STATUS" | grep -q "Up"; then
                echo "  ✅ $service: $CONTAINER_STATUS"
            else
                echo "  ❌ $service: $CONTAINER_STATUS"
            fi
        done
    else
        echo "  ⚠️  No services found or compose file issues"
    fi
    echo ""
else
    echo "❌ docker-compose-prod.yml not found"
    echo ""
fi

# Check system resources
echo "=== System Resources ==="
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h | grep -E "(Filesystem|/dev/|overlay)" | head -5
echo ""
echo "CPU load:"
uptime
echo ""

# Check recent application logs
echo "=== Recent Application Logs ==="
if command -v docker &> /dev/null && [ -f "docker-compose-prod.yml" ]; then
    MAIN_SERVICE=$(docker compose -f docker-compose-prod.yml ps --services 2>/dev/null | grep -E "(app|web|backend|cinema)" | head -1)
    if [ -n "$MAIN_SERVICE" ]; then
        echo "Last 15 lines from $MAIN_SERVICE:"
        docker compose -f docker-compose-prod.yml logs --tail 15 "$MAIN_SERVICE" 2>/dev/null || echo "Could not fetch logs for $MAIN_SERVICE"
    else
        echo "No main application service found"
        echo "Available services:"
        docker compose -f docker-compose-prod.yml ps --services 2>/dev/null || echo "No services found"
    fi
else
    echo "Docker or docker-compose-prod.yml not available for log checking"
fi

echo ""
echo "=== Network Connectivity ==="
# Check if main ports are listening
echo "Checking common application ports:"
netstat -tlnp 2>/dev/null | grep -E ":80|:443|:8000|:8080|:5432|:6379" || echo "netstat not available or no services on common ports"

echo ""
echo "=== Status Check Complete ==="
echo "Generated at: $(date)" 