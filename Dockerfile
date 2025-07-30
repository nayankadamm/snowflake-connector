FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libssl-dev libpq-dev build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY requirements.txt .
COPY snowflake_app.py .
COPY config.toml .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run the app
CMD ["python", "snowflake_app.py"]
    