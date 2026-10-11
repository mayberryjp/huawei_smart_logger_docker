FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir .

RUN useradd --create-home --no-log-init appuser
USER appuser

CMD ["python", "-m", "huawei_smart_logger"]