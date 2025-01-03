#!/bin/bash

# Configuration
APP_NAME="klipper-installer"
DEPLOY_DIR="/opt/$APP_NAME"
BACKUP_DIR="/opt/backups/$APP_NAME"
DOCKER_COMPOSE="docker-compose"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root"
    exit 1
fi

# Create directories if they don't exist
mkdir -p $DEPLOY_DIR
mkdir -p $BACKUP_DIR

# Backup current deployment
backup() {
    log "Creating backup..."
    BACKUP_FILE="$BACKUP_DIR/backup-$(date +'%Y%m%d-%H%M%S').tar.gz"
    tar -czf $BACKUP_FILE -C $DEPLOY_DIR . || {
        error "Backup failed"
        exit 1
    }
    log "Backup created at $BACKUP_FILE"
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."
    cd $DEPLOY_DIR
    $DOCKER_COMPOSE pull || {
        error "Failed to pull Docker images"
        exit 1
    }
}

# Stop services
stop_services() {
    log "Stopping services..."
    cd $DEPLOY_DIR
    $DOCKER_COMPOSE down || warn "Failed to stop some services"
}

# Start services
start_services() {
    log "Starting services..."
    cd $DEPLOY_DIR
    $DOCKER_COMPOSE up -d || {
        error "Failed to start services"
        exit 1
    }
}

# Check service health
check_health() {
    log "Checking service health..."
    local retries=0
    local max_retries=30
    local delay=2

    while [ $retries -lt $max_retries ]; do
        if curl -s http://localhost/api/health > /dev/null; then
            log "Services are healthy"
            return 0
        fi
        retries=$((retries + 1))
        sleep $delay
    done

    error "Health check failed after $max_retries attempts"
    return 1
}

# Cleanup old images and volumes
cleanup() {
    log "Cleaning up..."
    docker system prune -f
    
    # Keep only last 5 backups
    cd $BACKUP_DIR
    ls -t | tail -n +6 | xargs -r rm
}

# Rollback function
rollback() {
    error "Deployment failed, rolling back..."
    
    # Get latest backup
    LATEST_BACKUP=$(ls -t $BACKUP_DIR | head -n1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        cd $DEPLOY_DIR
        tar -xzf "$BACKUP_DIR/$LATEST_BACKUP" -C $DEPLOY_DIR
        start_services
        
        if [ $? -eq 0 ]; then
            log "Rollback successful"
        else
            error "Rollback failed"
        fi
    else
        error "No backup found for rollback"
    fi
}

# Main deployment process
main() {
    log "Starting deployment..."

    # Create backup
    backup

    # Stop services
    stop_services

    # Pull new images
    pull_images

    # Start services
    start_services

    # Check health
    if ! check_health; then
        rollback
        exit 1
    fi

    # Cleanup
    cleanup

    log "Deployment completed successfully"
}

# Execute main function
main

exit 0
