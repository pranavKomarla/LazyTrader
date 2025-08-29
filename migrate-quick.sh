#!/bin/bash

# Quick Prisma migration commands
# Usage: ./migrate-quick.sh [command]

case $1 in
    "create")
        echo "Creating migration..."
        docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate dev --name $2"
        ;;
    "deploy")
        echo "Applying migrations..."
        docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate deploy"
        ;;
    "generate")
        echo "Generating Prisma client..."
        docker-compose exec web sh -c "cd packages/NextAuth && npx prisma generate"
        ;;
    "studio")
        echo "Opening Prisma Studio..."
        docker-compose exec web sh -c "cd packages/NextAuth && npx prisma studio --port 5555 --hostname 0.0.0.0"
        ;;
    "status")
        echo "Migration status:"
        docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate status"
        ;;
    "reset")
        echo "⚠️  Resetting database..."
        docker-compose exec web sh -c "cd packages/NextAuth && npx prisma migrate reset --force"
        ;;
    *)
        echo "Usage: ./migrate-quick.sh [command]"
        echo ""
        echo "Commands:"
        echo "  create [name]  - Create new migration"
        echo "  deploy         - Apply pending migrations"
        echo "  generate       - Generate Prisma client"
        echo "  studio         - Open Prisma Studio"
        echo "  status         - Show migration status"
        echo "  reset          - Reset database (⚠️  DANGEROUS)"
        echo ""
        echo "Examples:"
        echo "  ./migrate-quick.sh create add-user-settings"
        echo "  ./migrate-quick.sh deploy"
        echo "  ./migrate-quick.sh studio"
        ;;
esac
