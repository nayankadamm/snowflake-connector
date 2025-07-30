FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app


# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libssl-dev libpq-dev build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt .
COPY config.toml .
COPY cve_2025_24793_poc.py .      
# ✅ Now this is your main app
COPY snowflake_connector_python-2.9.0-py3-none-any.whl .

# Install dependencies
RUN pip install --upgrade pip && \
    grep -v snowflake-connector-python requirements.txt > stripped.txt && \
    pip install -r stripped.txt && \
    pip install snowflake_connector_python-2.9.0-py3-none-any.whl

# Run the PoC script
CMD ["python", "cve_2025_24793_poc.py"]
