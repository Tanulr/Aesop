FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir -e .

# Copy API and examples (api.py at root)
COPY api.py .

EXPOSE 8080

# Cloud Run expects PORT env; uvicorn defaults to 8000
ENV PORT=8080
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT}
