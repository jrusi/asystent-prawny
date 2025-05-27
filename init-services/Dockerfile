FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY init.py .

# Copy backend code
COPY ../backend /app/backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run initialization script
CMD ["python", "init.py"]
