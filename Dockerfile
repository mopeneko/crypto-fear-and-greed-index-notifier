FROM python:3.12

RUN apt update && \
    apt upgrade -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN useradd -m notifier

USER notifier

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

ENTRYPOINT [ "poetry", "run", "python", "crypto_fear_and_greed_index_notifier/main.py" ]
