FROM python:3.12-alpine

RUN apk update --no-cache

RUN apk add --no-cache gcc musl-dev libffi-dev

RUN pip install --no-cache-dir poetry

RUN adduser -S notifier

USER notifier

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

ENTRYPOINT [ "poetry", "run", "python", "crypto_fear_and_greed_index_notifier/main.py" ]
