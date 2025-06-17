# Use Python 3.12 slim image as base
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m appuser
USER appuser
# Set working directory
WORKDIR /app

COPY --chown=appuser:appuser pyproject.toml .
COPY --chown=appuser:appuser uv.lock .
COPY --chown=appuser:appuser app app
COPY --chown=appuser:appuser views views
COPY --chown=appuser:appuser alembic alembic
COPY --chown=appuser:appuser alembic.ini alembic.ini
RUN uv sync 
# RUN source .venv/bin/activate
# RUN uv pip install -e .

# Create non-root user
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# Expose the port the app runs on
EXPOSE 4000
# Command to run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]