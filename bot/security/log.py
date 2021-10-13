from datetime import datetime
import discord
import discord.utils

client = discord.Client()

async def log_to_console(message, guild):
    channel_id = 897082239450484748
    channel = discord.utils.get(guild.channels, id=channel_id)
    now_time = datetime.now()

    error_embed = discord.Embed(title="Exception raised at - %s -" % (now_time.strftime("%H:%M:%S")), colour=discord.Colour.dark_red())
    error_embed.add_field(name="---------------", value=message, inline=False)
    await channel.send(embed=error_embed)

async def log_to_mod(message, guild, colour):
    channel_id = 897587711353954364
    channel = discord.utils.get(guild.channels, id=channel_id)
    now_time = datetime.now()

    log_embed = discord.Embed(title="Time = %s" % (now_time.strftime("%H:%M:%S")), colour=colour)
    log_embed.add_field(name="---------------", value=message, inline=False)
    await channel.send(embed=log_embed)