.PHONY: install dev-backend dev-frontend seed test test-backend test-frontend test-oracle lint format build docker-up docker-down

install:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm ci

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

seed:
	cd backend && python -m app.seed

test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm test

# Run the backend suite against a local Oracle (see docker-compose.yml).
test-oracle:
	cd backend && TEST_DATABASE_URL="oracle+oracledb://qa:qa_password@localhost:1521/?service_name=FREEPDB1" pytest

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint && npx prettier --check "src/**/*.{ts,tsx,css}"

format:
	cd backend && ruff check --fix . && ruff format .
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,css}"

build:
	cd frontend && npm run build

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
