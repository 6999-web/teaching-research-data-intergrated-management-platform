.PHONY: help install-frontend install-backend install dev-frontend dev-backend dev test-frontend test-backend test clean

help:
	@echo "Available commands:"
	@echo "  make install          - Install all dependencies"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo "  make install-backend  - Install backend dependencies"
	@echo "  make dev              - Start all services"
	@echo "  make dev-frontend     - Start frontend dev server"
	@echo "  make dev-backend      - Start backend dev server"
	@echo "  make test             - Run all tests"
	@echo "  make test-frontend    - Run frontend tests"
	@echo "  make test-backend     - Run backend tests"
	@echo "  make clean            - Clean build artifacts"

install: install-frontend install-backend

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && pip install -r requirements.txt

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

test-frontend:
	cd frontend && npm run test

test-backend:
	cd backend && pytest

test: test-frontend test-backend

clean:
	rm -rf frontend/node_modules frontend/dist
	rm -rf backend/__pycache__ backend/.pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
