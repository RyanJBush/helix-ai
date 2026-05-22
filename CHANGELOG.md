# Changelog

## v1.0.0 — May 2026
- Added a richer README with a Live Demo badge, screenshot section, data-pipeline Mermaid diagram, supported ticker list, and expanded tech-stack table.
- Added README discoverability keywords/tags for project topics.
- Added `docs/images/.gitkeep` to track screenshot directory structure.
- Added GitHub Actions CI workflow for Python 3.11, Ruff linting, and pytest smoke testing.

## 2026-05-14
- Added `BacktestEngine` service and `/backtesting/backtest` endpoint with return metrics, equity curve, and trade log.
- Added watchlist persistence model + `/watchlists` and `/watchlists/{id}/sentiment` aggregation endpoints.
- Added fear & greed composite service and `/market/fear-greed` endpoint.
- Added frontend Fear & Greed gauge and backtest results panel.
- Added root `pyproject.toml` and GitHub Actions CI workflow.
