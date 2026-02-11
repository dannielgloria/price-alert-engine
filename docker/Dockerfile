FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3

COPY pyproject.toml /app/
# No poetry.lock required for MVP; if you add it, copy it too.
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

COPY . /app

ENV PYTHONUNBUFFERED=1
CMD ["bash","-lc","uvicorn app.main:app --host 0.0.0.0 --port 8000"]
