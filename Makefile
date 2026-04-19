.PHONY: test-backend lint-backend run-backend lint-frontend test-frontend build-frontend format-frontend

test-backend:
cd backend && pytest -q

lint-backend:
cd backend && ruff check .

run-backend:
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

lint-frontend:
cd frontend && npm run lint

test-frontend:
cd frontend && npm run test -- --run

build-frontend:
cd frontend && npm run build

format-frontend:
cd frontend && npm run format
