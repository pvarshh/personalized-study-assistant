# Makefile for Personalized Study Assistant

.PHONY: help install run test clean docker-build docker-run lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies and set up environment"
	@echo "  run          - Run the Streamlit application"
	@echo "  demo         - Run the command-line demo"
	@echo "  test         - Run tests"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean temporary files and cache"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker services"

# Installation
install:
	python -m venv env
	./env/bin/pip install --upgrade pip
	./env/bin/pip install -r requirements.txt
	cp .env.example .env
	@echo "⚠️  Please edit .env file and add your Google Gemini API key"

# Development
run:
	./env/bin/streamlit run app.py

demo:
	./env/bin/python demo.py

test:
	./env/bin/python -m pytest tests/ -v

lint:
	./env/bin/flake8 src/ app.py demo.py
	./env/bin/mypy src/ --ignore-missing-imports

format:
	./env/bin/black src/ app.py demo.py
	./env/bin/isort src/ app.py demo.py

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf chroma_db
	rm -rf data/*.pdf data/*.docx data/*.pptx data/*.txt

# Docker
docker-build:
	docker build -t study-assistant .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development dependencies (optional)
install-dev:
	./env/bin/pip install black flake8 mypy isort pytest pytest-cov

# Production setup
setup-prod:
	pip install -r requirements.txt
	mkdir -p logs data chroma_db
	@echo "✅ Production environment ready"

# Backup
backup:
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		--exclude=env \
		--exclude=__pycache__ \
		--exclude=.git \
		--exclude=chroma_db \
		--exclude=data \
		.

# Update dependencies
update-deps:
	./env/bin/pip list --outdated
	@echo "Run 'pip install --upgrade <package>' to update specific packages"
