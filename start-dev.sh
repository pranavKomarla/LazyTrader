#!/bin/bash

# DESCRIPTION: This script starts the development environment for the LLM Project by starting the docker containers and running Prisma Studio
# It checks if Docker is running, and if the docker-compose.yml file exists
# It then starts the containers in detached mode
# It then waits for the containers to be ready
# It then runs Prisma Studio
# It then opens the browser to the Prisma Studio URL


# chmod +x start-dev.sh and run it with ./start-dev.sh to start the dev environment
# If you see errors, you may need to run it with sudo ./start-dev.sh to grant permissions
# After running, you can access the app at http://localhost:3000

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting LLM Project Development Environment${NC}"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

# Function to start Docker containers
start_containers() {
    echo -e "${BLUE}📦 Starting Docker containers...${NC}"
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${YELLOW}❌ docker-compose.yml not found in current directory${NC}"
        exit 1
    fi
    
    # Start containers in detached mode
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Docker containers started successfully!${NC}"
    else
        echo -e "${YELLOW}❌ Failed to start Docker containers${NC}"
        exit 1
    fi
}

# Function to wait for containers to be ready
wait_for_containers() {
    echo -e "${BLUE}⏳ Waiting for containers to be ready...${NC}"
    sleep 10
}

# Function to run Prisma Studio
run_prisma_studio() {
    echo -e "${BLUE}🗄️  Starting Prisma Studio...${NC}"
    
    # Check if Docker containers are running
    if ! docker-compose ps | grep -q "web.*Up"; then
        echo -e "${YELLOW}❌ Docker containers are not running. Please start them first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🎯 Starting Prisma Studio in Docker container...${NC}"
    echo -e "${BLUE}📊 Prisma Studio will be available at: http://localhost:5555${NC}"
    echo -e "${YELLOW}💡 Press Ctrl+C to stop Prisma Studio${NC}"
    
    # Run Prisma Studio inside Docker container
    docker-compose exec web npx prisma studio --port 5555 --hostname 0.0.0.0
}

# Main execution
main() {
    check_docker
    start_containers
    wait_for_containers
    #run_prisma_studio
}

# Run main function
main
