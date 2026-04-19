# Contributing

## Development

1. Start services:
   ```bash
   docker-compose up --build
   ```
2. Run backend tests:
   ```bash
   make test-backend
   ```
3. Run frontend lint/build:
   ```bash
   make lint-frontend && make build-frontend
   ```

## Pull Requests

- Keep changes focused and small.
- Ensure linting/tests pass before requesting review.
