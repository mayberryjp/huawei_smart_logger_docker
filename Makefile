.PHONY: install lint typecheck test security docker-build docker-run

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest -q

security:
	bandit -r src

docker-build:
	docker build -t mayberry4477/huawei_smart_logger_docker:dev .

docker-run:
	docker compose up