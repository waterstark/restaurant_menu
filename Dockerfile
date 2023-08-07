FROM python:3.10-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY ./poetry.lock .
COPY ./pyproject.toml .
RUN pip install poetry
RUN poetry install
COPY . .
# CMD ["poetry", "run","uvicorn", "python_code.main:app",  "--reload", "--host", "0.0.0.0", "--port", "8000"]
