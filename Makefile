.PHONY: install test lint build up clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/

lint:
	# Basic linting if tools available
	pip install ruff
	ruff check src/

build:
	docker build -t mcp-tw-invoice .

up:
	docker-compose up --build

clean:
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
