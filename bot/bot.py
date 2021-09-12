import discord
from discord import embeds
import discord.utils
import asyncio
import json

client = discord.Client()

with open("./properties.json") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]


@client.event
async def on_ready():
    print


client.run(TOKEN)
