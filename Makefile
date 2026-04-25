.PHONY: up down backend-dev frontend-dev lint test format

up:
	docker compose up --build

down:
	docker compose down -v

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd frontend && npm install && npm run dev

lint:
	cd frontend && npm install && npm run lint

test:
	cd backend && pip install -r requirements.txt && NLP_PROVIDER=heuristic PYTHONPATH=. pytest -q

format:
	@echo "Add formatters (ruff/prettier) as project evolves"
