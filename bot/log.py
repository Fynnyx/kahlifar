import discord
import discord.utils
import asyncio


async def log_to_console(message, guild):
    channel_id = 897082239450484748
    channel = discord.utils.get(guild.channels, id=channel_id)
    await channel.send(message)

