#!/bin/sh

# Define the Docker Compose files
COMPOSE_FILE="docker-compose.yml"
PRODUCTION_FILE="production.yml"

# Pull the latest images
echo "Pulling the latest images..."
docker-compose -f $COMPOSE_FILE -f $PRODUCTION_FILE pull

# Build the services
echo "Building the services..."
docker-compose -f $COMPOSE_FILE -f $PRODUCTION_FILE build

# Start all services
echo "Starting all services..."
docker-compose -f $COMPOSE_FILE -f $PRODUCTION_FILE up -d
