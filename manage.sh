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

db_start() {
    log "Starting PostgreSQL container..."
    if command -v podman-compose &> /dev/null; then
        podman-compose up -d postgres || podman-compose up -d
    elif command -v podman &> /dev/null; then
        podman run -d \
            --name scheduler-postgres \
            -e POSTGRES_DB=scheduler \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_PASSWORD=postgres \
            -p 5432:5432 \
            postgres:15
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