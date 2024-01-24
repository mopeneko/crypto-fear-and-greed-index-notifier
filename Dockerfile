FROM python:3.12-alpine

RUN apk update --no-cache

RUN apk add --no-cache gcc musl-dev

RUN pip install poetry

RUN adduser -S notifier

USER notifier

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

ENTRYPOINT [ "poetry", "run", "python", "crypto_fear_and_greed_index_notifier/main.py" ]
