# crypto-fear-and-greed-index-notifier

Notify Crypto Fear and Greed Index to Discord channel

## Requirements

- Python
- Poetry

## Installation

```sh
git clone https://github.com/mopeneko/crypto-fear-and-greed-index-notifier
cd crypto-fear-and-greed-index-notifier
poetry install
```

## Run

```sh
export DISCORD_TOKEN=YOUR_DISCORD_TOKEN
export DISCORD_CHANNEL_ID=YOUR_CHANNEL_ID
poetry run python crypto_fear_and_greed_index_notifier/main.py
```
