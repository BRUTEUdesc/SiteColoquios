#!/bin/sh

# Define the service name
SERVICE_NAME="web"

# Define the Docker Compose files
COMPOSE_FILE="docker-compose.yml"
PRODUCTION_FILE="docker-compose.prod.yml"

# Build the web service
echo "Building the $SERVICE_NAME service..."
docker-compose -f $COMPOSE_FILE -f $PRODUCTION_FILE build $SERVICE_NAME

# Recreate the web container
echo "Recreating the $SERVICE_NAME container..."
docker-compose -f $COMPOSE_FILE -f $PRODUCTION_FILE up -d --no-deps --force-recreate $SERVICE_NAME
