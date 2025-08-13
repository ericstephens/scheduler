#!/bin/bash

# manage.sh - Management script for scheduler project
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="scheduler"
ENV_FILE="$SCRIPT_DIR/environment.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if conda is available
check_conda() {
    if ! command -v conda &> /dev/null; then
        error "conda command not found. Please install conda/miniconda first."
        exit 1
    fi
}

# Check if environment exists
env_exists() {
    conda env list | grep -q "^$ENV_NAME "
}

# Create or update conda environment
setup_env() {
    log "Setting up conda environment..."
    check_conda
    
    if env_exists; then
        log "Environment '$ENV_NAME' exists. Updating from $ENV_FILE"
        conda env update -n "$ENV_NAME" -f "$ENV_FILE" --prune
    else
        log "Creating new environment '$ENV_NAME' from $ENV_FILE"
        conda env create -f "$ENV_FILE"
    fi
    
    success "Environment setup complete"
}

# Activate environment and run command
run_in_env() {
    check_conda
    
    if ! env_exists; then
        warn "Environment '$ENV_NAME' not found. Setting it up first..."
        setup_env
    fi
    
    log "Activating environment '$ENV_NAME' and running: $*"
    
    # Use conda run to execute in the environment
    conda run -n "$ENV_NAME" "$@"
}

# Database management functions
db_test() {
    log "Running database tests..."
    run_in_env python -m pytest src/database/test/ -v "$@"
}

db_test_coverage() {
    log "Running database tests with coverage..."
    run_in_env python -m pytest src/database/test/ --cov=src.database --cov-report=html --cov-report=term -v "$@"
}

# API management functions
api_test() {
    log "Running API tests..."
    TESTING=1 run_in_env python -m pytest src/api/test/ -v "$@"
}

api_test_coverage() {
    log "Running API tests with coverage..."
    TESTING=1 run_in_env python -m pytest src/api/test/ --cov=src.api --cov-report=html --cov-report=term -v "$@"
}

api_start() {
    log "Starting API server..."
    run_in_env python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
}

api_start_prod() {
    log "Starting API server in production mode..."
    run_in_env python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
}

# UI management functions
ui_start() {
    log "Starting UI development server..."
    cd "$SCRIPT_DIR/src/ui" && npm run dev
}

ui_stop() {
    log "Stopping UI development server..."
    # Find and kill processes running on common Vite ports (5173, 3000, 3001)
    local ports="5173 3000 3001"
    local killed=false
    
    for port in $ports; do
        local pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo $pids | xargs kill -TERM
            success "UI development server stopped (port $port)"
            killed=true
        fi
    done
    
    if [ "$killed" = false ]; then
        warn "No UI development server found running on ports: $ports"
    fi
}

# Combined test functions
test_all() {
    log "Running all tests..."
    TESTING=1 run_in_env python -m pytest src/database/test/ src/api/test/ -v "$@"
}

test_all_coverage() {
    log "Running all tests with coverage..."
    TESTING=1 run_in_env python -m pytest src/database/test/ src/api/test/ --cov=src --cov-report=html --cov-report=term -v "$@"
}

db_start() {
    log "Starting PostgreSQL container..."
    if command -v podman-compose &> /dev/null; then
        podman-compose up -d postgres || podman-compose up -d
    elif command -v podman &> /dev/null; then
        podman run -d \
            --name scheduler-postgres \
            -e POSTGRES_DB=scheduler \
            -e POSTGRES_USER=scheduler_user \
            -e POSTGRES_PASSWORD=scheduler_password \
            -p 5434:5432 \
            postgres:15-alpine
    else
        error "Neither podman-compose nor podman found. Please install podman."
        exit 1
    fi
    success "PostgreSQL container started"
}

db_stop() {
    log "Stopping PostgreSQL container..."
    if command -v podman-compose &> /dev/null; then
        podman-compose down
    elif command -v podman &> /dev/null; then
        podman stop scheduler-postgres || true
        podman rm scheduler-postgres || true
    fi
    success "PostgreSQL container stopped"
}

db_restart() {
    db_stop
    sleep 2
    db_start
}

db_shell() {
    log "Connecting to PostgreSQL shell..."
    run_in_env python -c "
from src.database.connection import get_database_url
import subprocess
import sys

url = get_database_url()
print(f'Connecting to: {url}')

# Extract connection details
import urllib.parse as urlparse
parsed = urlparse.urlparse(url)

cmd = [
    'podman', 'exec', '-it', 'scheduler-postgres',
    'psql', '-U', parsed.username, '-d', parsed.path[1:]  # Remove leading slash
]

try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f'Error connecting to database: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Show usage
usage() {
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Environment Management:"
    echo "  setup-env          Create or update conda environment"
    echo ""
    echo "Database Commands:"
    echo "  db-test [args]     Run database tests (with optional pytest args)"
    echo "  db-test-coverage   Run database tests with coverage report"
    echo "  db-start          Start PostgreSQL container"
    echo "  db-stop           Stop PostgreSQL container"
    echo "  db-restart        Restart PostgreSQL container"
    echo "  db-shell          Connect to PostgreSQL shell"
    echo ""
    echo "API Commands:"
    echo "  api-test [args]    Run API tests (with optional pytest args)"
    echo "  api-test-coverage  Run API tests with coverage report"
    echo "  api-start         Start API development server"
    echo "  api-start-prod    Start API production server"
    echo ""
    echo "UI Commands:"
    echo "  ui-start          Start UI development server"
    echo "  ui-stop           Stop UI development server"
    echo ""
    echo "Testing Commands:"
    echo "  test-all          Run all tests (database + API)"
    echo "  test-all-coverage Run all tests with coverage report"
    echo ""
    echo "General Commands:"
    echo "  run <command>     Run any command in the conda environment"
    echo ""
    echo "Examples:"
    echo "  $0 db-test                          # Run all database tests"
    echo "  $0 db-test -k test_instructor       # Run only instructor tests"
    echo "  $0 db-test-coverage                 # Run tests with coverage"
    echo "  $0 run python -c 'import sys; print(sys.version)'"
    echo ""
}

# Main command dispatcher
case "${1:-}" in
    setup-env)
        setup_env
        ;;
    db-test)
        shift
        db_test "$@"
        ;;
    db-test-coverage)
        shift
        db_test_coverage "$@"
        ;;
    db-start)
        db_start
        ;;
    db-stop)
        db_stop
        ;;
    db-restart)
        db_restart
        ;;
    db-shell)
        db_shell
        ;;
    api-test)
        shift
        api_test "$@"
        ;;
    api-test-coverage)
        shift
        api_test_coverage "$@"
        ;;
    api-start)
        api_start
        ;;
    api-start-prod)
        api_start_prod
        ;;
    ui-start)
        ui_start
        ;;
    ui-stop)
        ui_stop
        ;;
    test-all)
        shift
        test_all "$@"
        ;;
    test-all-coverage)
        shift
        test_all_coverage "$@"
        ;;
    run)
        shift
        run_in_env "$@"
        ;;
    help|--help|-h)
        usage
        ;;
    "")
        error "No command specified"
        usage
        exit 1
        ;;
    *)
        error "Unknown command: $1"
        usage
        exit 1
        ;;
esac