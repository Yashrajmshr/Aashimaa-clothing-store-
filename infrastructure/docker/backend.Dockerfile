FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for build, libpq, and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source code
COPY backend /app/backend

# Create media directories
RUN mkdir -p /app/backend/media/qr_codes /app/backend/media/invoices /app/backend/media/garment_photos

ENV PYTHONPATH=/app
ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ready || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
