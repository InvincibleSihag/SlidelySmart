# Slidely PPT Generator — production image
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies only (no app code yet)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY alembic ./alembic
COPY alembic.ini .
COPY app ./app
COPY prompts ./prompts
COPY templates ./templates
COPY skills ./skills

ENV PORT=8080
EXPOSE 8080

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default: run FastAPI. Override CMD for Celery worker.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
