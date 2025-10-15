.PHONY: help start stop restart logs clean rebuild status

help: ## Show this help message
	@echo "AI-Powered Financial System - Make Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

start: ## Start the entire system (postgres → data pipeline → backend → frontend)
	@./start.sh

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	@docker compose down
	@echo "✅ All services stopped"

restart: ## Restart all services (will reload data)
	@echo "🔄 Restarting system..."
	@$(MAKE) stop
	@sleep 2
	@$(MAKE) start

logs: ## View logs from all services
	@docker compose logs -f

logs-backend: ## View backend logs only
	@docker compose logs -f backend

logs-frontend: ## View frontend logs only
	@docker compose logs -f frontend

logs-postgres: ## View PostgreSQL logs only
	@docker compose logs -f postgres

clean: ## Stop services and remove volumes (deletes all data)
	@echo "⚠️  WARNING: This will delete all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		echo "✅ Cleaned up all containers and volumes"; \
	else \
		echo "❌ Cancelled"; \
	fi

rebuild: ## Rebuild all containers and restart
	@echo "🔨 Rebuilding containers..."
	@docker compose build --no-cache
	@$(MAKE) start

status: ## Check status of all services
	@echo "📊 Service Status:"
	@docker compose ps

shell-backend: ## Open shell in backend container
	@docker compose exec backend /bin/bash

shell-postgres: ## Open PostgreSQL shell
	@docker compose exec postgres psql -U postgres -d financial_data

pipeline: ## Run data pipeline only (reloads data from separate data_pipeline project)
	@echo "📥 Running data pipeline (separate Python project)..."
	@cd data_pipeline && \
	if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
		. venv/bin/activate && pip install -q -r requirements.txt; \
	fi && \
	. venv/bin/activate && \
	python main.py init && \
	python main.py run && \
	echo "✅ Data pipeline completed!"

check-data: ## Check how many records are in the database
	@echo "📊 Database Record Count:"
	@docker compose exec -T postgres psql -U postgres -d financial_data -c "SELECT COUNT(*) as total_records FROM fact_financials;"

test-backend: ## Run backend tests
	@docker compose exec backend pytest

test-api: ## Test API health
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8000/health | jq
	@echo ""
	@curl -s http://localhost:8000/api/dashboard/overview | jq '.profit_loss | length'

dev: ## Start in development mode with live reload
	@echo "🔧 Starting in development mode..."
	@docker compose up

build: ## Build all containers
	@docker compose build
