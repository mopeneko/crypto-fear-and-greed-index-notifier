FROM python:3.12

WORKDIR /app

RUN apt update && apt upgrade -y && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

ENTRYPOINT [ "poetry", "run", "python", "crypto_fear_and_greed_index_notifier/main.py" ]
