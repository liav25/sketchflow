FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including Node.js for mermaid-cli)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    ca-certificates \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Mermaid CLI globally
RUN npm install -g @mermaid-js/mermaid-cli

# Optional: set mmdc path for the validator
ENV MMDC_BIN=/usr/local/bin/mmdc

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p storage/uploads storage/previews storage/temp

# Expose port
EXPOSE 8000

# Ensure logs are unbuffered for real-time streaming
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
