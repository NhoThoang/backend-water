# Makefile for managing Docker Compose services
# Directories
BACKEND_DIR = backend
FRONTEND_DIR = frontend
NGINX_DIR = nginx
DB_DIR = database_server

# Commands
DOCKER_COMPOSE = docker compose
NETWORK_NAME = app_network

.PHONY: all up down pull restart status network logs-backend logs-frontend logs-db logs-nginx

# Default target: Start all services
all: up

# Create network if not exists
network:
	@docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || docker network create $(NETWORK_NAME)

# Pull images for all services
pull:
	@echo "Pulling images..."
	cd $(DB_DIR) && $(DOCKER_COMPOSE) pull
	cd $(BACKEND_DIR) && $(DOCKER_COMPOSE) pull
	cd $(FRONTEND_DIR) && $(DOCKER_COMPOSE) pull
	cd $(NGINX_DIR) && $(DOCKER_COMPOSE) pull

# Start all services
up: network
	@echo "Starting services..."
	cd $(DB_DIR) && $(DOCKER_COMPOSE) up -d
	cd $(BACKEND_DIR) && $(DOCKER_COMPOSE) up -d
	cd $(FRONTEND_DIR) && $(DOCKER_COMPOSE) up -d
	cd $(NGINX_DIR) && $(DOCKER_COMPOSE) up -d

# Stop all services
down:
	@echo "Stopping services..."
	cd $(NGINX_DIR) && $(DOCKER_COMPOSE) down
	cd $(FRONTEND_DIR) && $(DOCKER_COMPOSE) down
	cd $(BACKEND_DIR) && $(DOCKER_COMPOSE) down
	cd $(DB_DIR) && $(DOCKER_COMPOSE) down

# Restart all services
restart: down up

# Show status of all services
status:
	@echo "=== Database Status ==="
	cd $(DB_DIR) && $(DOCKER_COMPOSE) ps
	@echo "\n=== Backend Status ==="
	cd $(BACKEND_DIR) && $(DOCKER_COMPOSE) ps
	@echo "\n=== Frontend Status ==="
	cd $(FRONTEND_DIR) && $(DOCKER_COMPOSE) ps
	@echo "\n=== Nginx Status ==="
	cd $(NGINX_DIR) && $(DOCKER_COMPOSE) ps

# View logs
logs-backend:
	cd $(BACKEND_DIR) && $(DOCKER_COMPOSE) logs -f

logs-frontend:
	cd $(FRONTEND_DIR) && $(DOCKER_COMPOSE) logs -f

logs-db:
	cd $(DB_DIR) && $(DOCKER_COMPOSE) logs -f

logs-nginx:
	cd $(NGINX_DIR) && $(DOCKER_COMPOSE) logs -f
