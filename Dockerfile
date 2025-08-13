FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY src/ ./src/
COPY README.md ./

# Install Poetry
RUN pip install poetry

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main

# Use a flexible entrypoint that can run either mode
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose HTTP port for HTTP mode
EXPOSE 8000

# Default to stdio mode for backward compatibility, but allow override
ENTRYPOINT ["/entrypoint.sh"]
CMD ["stdio"]
