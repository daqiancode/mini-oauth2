# Use Python 3.12 slim image as base
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies
# RUN uv sync
# Copy application code
COPY app app
COPY views views
COPY alembic alembic
COPY alembic.ini alembic.ini
RUN uv sync 
# RUN source .venv/bin/activate
# RUN uv pip install -e .

# Create non-root user
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# Expose the port the app runs on
EXPOSE 3000
# Command to run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]