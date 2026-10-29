.PHONY: help install test up down logs reset

help:  ## show commands
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-8s %s\n", $$1, $$2}'

install:  ## install dependencies locally
	uv sync

test:  ## run tests (no docker needed)
	uv run pytest

up:  ## start api, worker and redis (http://localhost:8000/docs)
	docker compose up --build -d
	@echo "api: http://localhost:8000/docs"

down:  ## stop everything
	docker compose down

logs:  ## follow api and worker logs
	docker compose logs -f api worker

reset:  ## stop everything and wipe the database
	docker compose down -v
