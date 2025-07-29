#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Create test-reports directory if it doesn't exist
mkdir -p test-reports

print_header() {
    echo -e "\n${BLUE}===========================================================${NC}"
    echo -e "${BLUE} $1 ${NC}"
    echo -e "${BLUE}===========================================================${NC}\n"
}

show_help() {
    echo -e "${YELLOW}PyLLM Docker Testing Environment${NC}"
    echo -e "\nUsage: $0 [options]\n"
    echo -e "Options:"
    echo -e "  --build\t\tBuild Docker images before starting"
    echo -e "  --run-tests\t\tRun all tests automatically after starting"
    echo -e "  --interactive\t\tStart in interactive mode (don't run tests automatically)"
    echo -e "  --mock-service\t\tStart the mock service only"
    echo -e "  --stop\t\tStop and remove containers"
    echo -e "  --clean\t\tStop containers and remove volumes"
    echo -e "  --help\t\tShow this help message"
    echo -e "\nExamples:\n"
    echo -e "  $0 --build --run-tests\t# Build and run all tests"
    echo -e "  $0 --interactive\t\t# Start in interactive mode"
    echo -e "  $0 --mock-service\t\t# Start mock service only"
    echo -e "  $0 --stop\t\t# Stop containers"
}

# Default options
BUILD=false
RUN_TESTS=false
INTERACTIVE=false
MOCK_SERVICE=false
STOP=false
CLEAN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD=true
            shift
            ;;
        --run-tests)
            RUN_TESTS=true
            shift
            ;;
        --interactive)
            INTERACTIVE=true
            shift
            ;;
        --mock-service)
            MOCK_SERVICE=true
            shift
            ;;
        --stop)
            STOP=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Stop containers if requested
if [ "$STOP" = true ]; then
    print_header "Stopping Docker containers"
    docker-compose -f docker-compose.test.yml down
    echo -e "${GREEN}Containers stopped${NC}"
    exit 0
fi

# Clean containers and volumes if requested
if [ "$CLEAN" = true ]; then
    print_header "Cleaning Docker containers and volumes"
    docker-compose -f docker-compose.test.yml down -v
    echo -e "${GREEN}Containers and volumes removed${NC}"
    exit 0
fi

# Build and start containers
if [ "$BUILD" = true ]; then
    print_header "Building Docker images"
    docker-compose -f docker-compose.test.yml build
fi

# Start the mock service
if [ "$MOCK_SERVICE" = true ]; then
    print_header "Starting PyLLM mock service"
    docker-compose -f docker-compose.test.yml up -d getllm-mock
    
    # Wait for the service to be ready
    echo -e "${YELLOW}Waiting for mock service to start...${NC}"
    sleep 5
    
    # Check if the service is running
    SERVICE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health)
    if [ "$SERVICE_STATUS" = "200" ]; then
        echo -e "${GREEN}PyLLM mock service is running${NC}"
    else
        echo -e "${RED}Failed to start PyLLM mock service (status code: $SERVICE_STATUS)${NC}"
        exit 1
    fi
    
    echo -e "\n${YELLOW}Mock service is running at http://localhost:8002${NC}"
    echo -e "${YELLOW}To stop the service, run:${NC} $0 --stop"
    exit 0
fi

# Run tests if requested
if [ "$RUN_TESTS" = true ]; then
    print_header "Running PyLLM tests"
    docker-compose -f docker-compose.test.yml up getllm-test
    exit 0
fi

# Start interactive mode if requested
if [ "$INTERACTIVE" = true ] || [ "$RUN_TESTS" = false -a "$MOCK_SERVICE" = false ]; then
    print_header "Starting interactive mode"
    echo -e "${YELLOW}Available commands:${NC}"
    echo -e "  ${GREEN}python -m pytest tests/ -v${NC} - Run all tests"
    echo -e "  ${GREEN}python -m getllm.app --port 8002 --host 0.0.0.0${NC} - Start the PyLLM service"
    echo -e "\n${YELLOW}Type 'exit' to exit the container${NC}\n"
    
    docker-compose -f docker-compose.test.yml run --rm getllm-test bash
fi

echo -e "\n${YELLOW}To stop the containers, run:${NC} $0 --stop"
echo -e "${YELLOW}To clean up containers and volumes, run:${NC} $0 --clean"
