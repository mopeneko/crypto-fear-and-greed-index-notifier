import os
import discord
from discord.ext import tasks
import httpx

from coinglass import fetch_long_short_rate


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = None

    async def setup_hook(self):
        self.notify_fear_greed.start()
        self.notify_long_short_ratio.start()

    async def on_ready(self):
        print(f"Logged in as {self.user}({self.user.id})")

    @tasks.loop(hours=1)
    async def notify_fear_greed(self):
        channel = self.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))

        async with httpx.AsyncClient() as client:
            res = await client.get("https://api.coin-stats.com/v2/fear-greed")
            if res.is_error:
                await channel.send("Failed to get Crypto Fear and Greed Index.")

            data = res.json()
            now = data["now"]
            timestamp = now["timestamp"]

            if timestamp == self.timestamp:
                return

            self.timestamp = timestamp

            value = now["value"]
            value_classification = now["value_classification"]

            await channel.send(
                f"[Crypto Fear and Greed Index]\n{value} - {value_classification}"
            )

    @notify_fear_greed.before_loop
    async def before_notify_fear_greed(self):
        await self.wait_until_ready()

    @tasks.loop(hours=1)
    async def notify_long_short_ratio(self):
        channel = self.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))

        data = fetch_long_short_rate()[0]
        binance_data = [d for d in data["list"] if d["exchangeName"] == "Binance"][0]
        okx_data = [d for d in data["list"] if d["exchangeName"] == "OKX"][0]
        bybit_data = [d for d in data["list"] if d["exchangeName"] == "Bybit"][0]

        obj = {
            "All": data,
            "Binance": binance_data,
            "OKX": okx_data,
            "Bybit": bybit_data
        }

        text = "[BTC Long/Short Ratio]\n"
        for k, v in obj.items():
            long_rate = v["longRate"]
            short_rate = v["shortRate"]
            text += f"\n[{k}]\nLong {long_rate} % / Short {short_rate} %"

        await channel.send(text)

    @notify_long_short_ratio.before_loop
    async def before_notify_long_short_ratio(self):
        await self.wait_until_ready()


client = MyClient(intents=discord.Intents.default())
client.run(os.getenv("DISCORD_TOKEN"))
