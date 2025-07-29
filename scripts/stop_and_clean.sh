#!/bin/sh

# Define the service name
SERVICE_NAME="web"

# Define the Docker Compose files
COMPOSE_FILE="docker-compose.yml"
PRODUCTION_FILE="docker-compose.prod.yml"

# Stop the web service and its dependencies
echo "Stopping the $SERVICE_NAME service and its dependencies..."
docker compose -f $COMPOSE_FILE -f $PRODUCTION_FILE stop $SERVICE_NAME

# Remove all services
echo "Removing the $SERVICE_NAME container and its dependencies..."
docker compose -f $COMPOSE_FILE -f $PRODUCTION_FILE down
