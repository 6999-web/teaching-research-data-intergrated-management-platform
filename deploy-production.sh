#!/bin/bash
# Production Deployment Script
# 生产环境部署脚本

set -e

echo "=========================================="
echo "Teaching Office Evaluation System"
echo "Production Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run this script as root"
    exit 1
fi

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    print_error "backend/.env file not found"
    echo "Please create backend/.env from backend/.env.production template"
    exit 1
fi
print_success "Environment file exists"

# Check if SSL certificates exist
if [ ! -f "ssl/teaching-office.crt" ] || [ ! -f "ssl/teaching-office.key" ]; then
    print_warning "SSL certificates not found in ssl/ directory"
    read -p "Do you want to generate self-signed certificates for testing? (yes/no): " GENERATE_SSL
    if [ "$GENERATE_SSL" = "yes" ]; then
        echo "Generating self-signed SSL certificates..."
        mkdir -p ssl
        openssl req -new -x509 -days 365 -nodes \
            -out ssl/teaching-office.crt \
            -keyout ssl/teaching-office.key \
            -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
        chmod 644 ssl/teaching-office.crt
        chmod 600 ssl/teaching-office.key
        print_success "Self-signed certificates generated"
    else
        print_error "SSL certificates are required. Please add them to ssl/ directory"
        exit 1
    fi
else
    print_success "SSL certificates found"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p backups/postgres
mkdir -p backups/minio
mkdir -p backend/logs
print_success "Directories created"

# Make backup scripts executable
echo ""
echo "Setting up backup scripts..."
chmod +x scripts/*.sh
print_success "Backup scripts configured"

# Confirm deployment
echo ""
echo "=========================================="
echo "Ready to deploy!"
echo "=========================================="
echo ""
read -p "Do you want to proceed with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Pull latest images
echo ""
echo "Pulling latest Docker images..."
docker-compose -f docker-compose.production.yml pull

# Build services
echo ""
echo "Building services..."
docker-compose -f docker-compose.production.yml build

# Start services
echo ""
echo "Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "Checking service status..."
docker-compose -f docker-compose.production.yml ps

# Run database migrations
echo ""
echo "Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T backend alembic upgrade head

# Verify deployment
echo ""
echo "=========================================="
echo "Verifying deployment..."
echo "=========================================="

# Check if backend is responding
if docker-compose -f docker-compose.production.yml exec -T backend curl -f http://localhost:8000/api/health &> /dev/null; then
    print_success "Backend is healthy"
else
    print_error "Backend health check failed"
fi

# Check if frontend is responding
if docker-compose -f docker-compose.production.yml exec -T frontend curl -f http://localhost/health &> /dev/null; then
    print_success "Frontend is healthy"
else
    print_error "Frontend health check failed"
fi

# Check if database is responding
if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U teaching_office_user &> /dev/null; then
    print_success "Database is healthy"
else
    print_error "Database health check failed"
fi

# Display logs
echo ""
echo "=========================================="
echo "Recent logs:"
echo "=========================================="
docker-compose -f docker-compose.production.yml logs --tail=20

# Final message
echo ""
echo "=========================================="
echo "Deployment completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify the application is accessible at https://your-domain.com"
echo "2. Check logs: docker-compose -f docker-compose.production.yml logs -f"
echo "3. Monitor services: docker-compose -f docker-compose.production.yml ps"
echo "4. Review DEPLOYMENT_GUIDE.md for post-deployment tasks"
echo ""
echo "To stop services: docker-compose -f docker-compose.production.yml down"
echo "To view logs: docker-compose -f docker-compose.production.yml logs -f"
echo ""
