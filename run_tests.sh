#!/bin/bash

# SmartPrint Pro - Test Runner Script
# This script helps run the test suite with various options

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}SmartPrint Pro - Test Suite${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest is not installed. Installing test dependencies...${NC}"
    pip install pytest pytest-cov pytest-flask
    echo ""
fi

# Parse command line arguments
case "${1:-all}" in
    all)
        echo -e "${GREEN}Running all tests...${NC}"
        pytest -v
        ;;
    
    coverage)
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest --cov=. --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    auth)
        echo -e "${GREEN}Running authentication tests...${NC}"
        pytest tests/test_authentication.py -v
        ;;
    
    models)
        echo -e "${GREEN}Running model tests...${NC}"
        pytest tests/test_models.py -v
        ;;
    
    routes)
        echo -e "${GREEN}Running route tests...${NC}"
        pytest tests/test_routes.py -v
        ;;
    
    orders)
        echo -e "${GREEN}Running order tests...${NC}"
        pytest tests/test_orders.py -v
        ;;
    
    vendor)
        echo -e "${GREEN}Running vendor workflow tests...${NC}"
        pytest tests/test_vendor_workflow.py -v
        ;;
    
    admin)
        echo -e "${GREEN}Running admin tests...${NC}"
        pytest tests/test_admin.py -v
        ;;
    
    integration)
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest tests/test_integration.py -v
        ;;
    
    utils)
        echo -e "${GREEN}Running utility tests...${NC}"
        pytest tests/test_utils.py -v
        ;;
    
    fast)
        echo -e "${GREEN}Running fast tests only...${NC}"
        pytest -v -m "not slow"
        ;;
    
    failed)
        echo -e "${GREEN}Re-running failed tests...${NC}"
        pytest --lf -v
        ;;
    
    debug)
        echo -e "${GREEN}Running tests with detailed output...${NC}"
        pytest -vv -s
        ;;
    
    watch)
        echo -e "${GREEN}Watching for changes and running tests...${NC}"
        echo -e "${YELLOW}(Press Ctrl+C to stop)${NC}"
        pytest-watch
        ;;
    
    install)
        echo -e "${GREEN}Installing test dependencies...${NC}"
        pip install pytest pytest-cov pytest-flask pytest-watch
        echo -e "${GREEN}Dependencies installed successfully!${NC}"
        ;;
    
    help|--help|-h)
        echo "Usage: ./run_tests.sh [command]"
        echo ""
        echo "Commands:"
        echo "  all           Run all tests (default)"
        echo "  coverage      Run tests with coverage report"
        echo "  auth          Run authentication tests"
        echo "  models        Run model tests"
        echo "  routes        Run route tests"
        echo "  orders        Run order tests"
        echo "  vendor        Run vendor workflow tests"
        echo "  admin         Run admin tests"
        echo "  integration   Run integration tests"
        echo "  utils         Run utility tests"
        echo "  fast          Run fast tests only (skip slow tests)"
        echo "  failed        Re-run only failed tests"
        echo "  debug         Run with detailed output"
        echo "  watch         Watch for changes and auto-run tests"
        echo "  install       Install test dependencies"
        echo "  help          Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                  # Run all tests"
        echo "  ./run_tests.sh coverage         # Run with coverage"
        echo "  ./run_tests.sh vendor           # Run vendor tests only"
        echo "  ./run_tests.sh debug            # Run with detailed output"
        ;;
    
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}==================================${NC}"
echo -e "${GREEN}Test run complete!${NC}"
echo -e "${BLUE}==================================${NC}"
