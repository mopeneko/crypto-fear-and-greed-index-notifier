import os
import discord
from discord.ext import tasks
import httpx
from coinglass import fetch_funding_rate, fetch_long_short_rate


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = None

    async def setup_hook(self):
        self.notify_fear_greed.start()
        self.notify_long_short_ratio.start()
        self.notify_funding_rate.start()

    async def on_ready(self):
        print(f"Logged in as {self.user}({self.user.id})")

    @tasks.loop(minutes=10)
    async def notify_fear_greed(self):
        channel = self.get_channel(int(os.getenv("DISCORD_CHANNEL_ID_FEAR_AND_GREED")))

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

    @tasks.loop(minutes=10)
    async def notify_long_short_ratio(self):
        channel = self.get_channel(int(os.getenv("DISCORD_CHANNEL_ID_LONG_SHORT_RATIO")))

        data = fetch_long_short_rate()[0]
        binance_data = [d for d in data["list"] if d["exchangeName"] == "Binance"][0]
        okx_data = [d for d in data["list"] if d["exchangeName"] == "OKX"][0]
        bybit_data = [d for d in data["list"] if d["exchangeName"] == "Bybit"][0]

        obj = {
            "All": data,
            "Binance": binance_data,
            "OKX": okx_data,
            "Bybit": bybit_data,
        }

        text = "[BTC Long/Short Ratio]\n"
        for k, v in obj.items():
            long_vol = v["longVolUsd"]
            short_vol = v["shortVolUsd"]
            ratio = round(long_vol / short_vol, 2)
            long_rate = v["longRate"]
            short_rate = v["shortRate"]
            text += f"\n[{k}]\n{ratio} - Long {long_rate} % / Short {short_rate} %"

        await channel.send(text)

    @notify_long_short_ratio.before_loop
    async def before_notify_long_short_ratio(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=10)
    async def notify_funding_rate(self):
        channel = self.get_channel(int(os.getenv("DISCORD_CHANNEL_ID_FUNDING_RATE")))

        data = fetch_funding_rate()

        dict_ = {}

        for d in data:
            if d["symbol"] != "BTC":
                continue

            for c_margin in d["cMarginList"]:
                if (
                    not (
                        "exchangeName" in c_margin.keys() and "rate" in c_margin.keys()
                    )
                    or c_margin["exchangeName"] in dict_.keys()
                ):
                    continue
                dict_[c_margin["exchangeName"]] = c_margin["rate"]

        text = "[BTC Funding Rate]\n"
        for k, v in dict_.items():
            text += f"\n{k} {v} %"

        await channel.send(text)

    @notify_funding_rate.before_loop
    async def before_notify_funding_rate(self):
        await self.wait_until_ready()


client = MyClient(intents=discord.Intents.default())
client.run(os.getenv("DISCORD_TOKEN"))
