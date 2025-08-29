#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️  Prisma Migration Script${NC}"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

# Function to check if containers are running
check_containers() {
    if ! docker-compose ps | grep -q "web.*Up"; then
        echo -e "${YELLOW}⚠️  Docker containers are not running. Starting them...${NC}"
        docker-compose up -d
        sleep 10
    fi
}

# Function to create a new migration
create_migration() {
    echo -e "${BLUE}📝 Creating new migration...${NC}"
    
    # Get migration name from user
    read -p "Enter migration name (e.g., add-user-settings): " migration_name
    
    if [ -z "$migration_name" ]; then
        echo -e "${RED}❌ Migration name cannot be empty${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔄 Creating migration: $migration_name${NC}"
    
    # Create migration inside Docker container
    docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate dev --name $migration_name"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Migration created successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to create migration${NC}"
        exit 1
    fi
}

# Function to apply pending migrations
apply_migrations() {
    echo -e "${BLUE}🔄 Applying pending migrations...${NC}"
    
    # Apply migrations inside Docker container
    docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate deploy"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Migrations applied successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to apply migrations${NC}"
        exit 1
    fi
}

# Function to reset database
reset_database() {
    echo -e "${YELLOW}⚠️  WARNING: This will reset your database and lose all data!${NC}"
    read -p "Are you sure you want to continue? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🔄 Resetting database...${NC}"
        
        # Reset database inside Docker container
        docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate reset --force"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database reset successfully!${NC}"
        else
            echo -e "${RED}❌ Failed to reset database${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}🛑 Database reset cancelled${NC}"
    fi
}

# Function to generate Prisma client
generate_client() {
    echo -e "${BLUE}🔧 Generating Prisma client...${NC}"
    
    # Generate client inside Docker container
    docker-compose exec web sh -c "cd packages/NextAuth && npx prisma generate"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Prisma client generated successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to generate Prisma client${NC}"
        exit 1
    fi
}

# Function to show migration status
show_status() {
    echo -e "${BLUE}📊 Migration status:${NC}"
    
    # Show status inside Docker container
    docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate status"
}

# Function to show database schema
show_schema() {
    echo -e "${BLUE}📋 Current database schema:${NC}"
    
    # Show schema inside Docker container
    docker-compose exec web sh -c "cd packages/NextAuth && npx prisma db pull --print"
}

# Function to open Prisma Studio
open_studio() {
    echo -e "${BLUE}🎯 Opening Prisma Studio...${NC}"
    echo -e "${GREEN}📊 Prisma Studio will be available at: http://localhost:5555${NC}"
    echo -e "${YELLOW}💡 Press Ctrl+C to stop Prisma Studio${NC}"
    
    # Open Prisma Studio inside Docker container
    docker-compose exec web sh -c "cd packages/NextAuth && npx prisma studio --port 5555 --hostname 0.0.0.0"
}

# Main menu
show_menu() {
    echo -e "\n${BLUE}🔧 Prisma Migration Menu:${NC}"
    echo -e "1) Create new migration"
    echo -e "2) Apply pending migrations"
    echo -e "3) Generate Prisma client"
    echo -e "4) Show migration status"
    echo -e "5) Show database schema"
    echo -e "6) Reset database (⚠️  DANGEROUS)"
    echo -e "7) Open Prisma Studio"
    echo -e "8) Exit"
    echo -e ""
}

# Main execution
main() {
    check_docker
    check_containers
    
    while true; do
        show_menu
        read -p "Select an option (1-8): " choice
        
        case $choice in
            1)
                create_migration
                ;;
            2)
                apply_migrations
                ;;
            3)
                generate_client
                ;;
            4)
                show_status
                ;;
            5)
                show_schema
                ;;
            6)
                reset_database
                ;;
            7)
                open_studio
                ;;
            8)
                echo -e "${GREEN}👋 Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid option. Please select 1-8.${NC}"
                ;;
        esac
        
        echo -e "\n${BLUE}Press Enter to continue...${NC}"
        read
    done
}

# Run main function
main
