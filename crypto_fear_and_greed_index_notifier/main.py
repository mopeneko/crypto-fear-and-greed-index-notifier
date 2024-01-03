import os
import discord
from discord.ext import tasks
import httpx


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = None

    async def setup_hook(self):
        self.notify.start()

    async def on_ready(self):
        print(f"Logged in as {self.user}({self.user.id})")

    @tasks.loop(hours=1)
    async def notify(self):
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

            self.timestamp = self.timestamp

            value = now["value"]
            value_classification = now["value_classification"]

            await channel.send(
                f"[Crypto Fear and Greed Index]\n{value} - {value_classification}"
            )

    @notify.before_loop
    async def before_notify(self):
        await self.wait_until_ready()


client = MyClient(intents=discord.Intents.default())
client.run(os.getenv("DISCORD_TOKEN"))
