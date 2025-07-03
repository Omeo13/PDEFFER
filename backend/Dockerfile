FROM python:3.12-slim

WORKDIR /app

# Copy dependency files first for better cache usage
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry



# Install dependencies without creating a virtual environment
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi

# Copy the rest of the backend source code, excluding 'data' (excluded via .dockerignore)
COPY . /app

# Expose the FastAPI port
EXPOSE 8000

# Start the FastAPI app with live reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
