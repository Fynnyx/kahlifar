from asyncio.protocols import DatagramProtocol
import discord
from discord import embeds
from discord import channel

from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure

# from discord_slash import SlashCommand, SlashContext

import discord.utils

import asyncio
import json



with open("properties.json") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]
PREFIX = data["properties"]["prefix"]

discord_link = data["properties"]["discord_link"]
server_ip = data["properties"]["server_ip"]



client = commands.Bot(command_prefix=PREFIX)



@client.event
async def on_ready():
    print("Kahlifar: logged in")
    client.loop.create_task(status_task())


async def status_task():
    messages = data["properties"]["status"]["messages"]
    time = data["properties"]["status"]["time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(messages[x]), status=discord.Status.online)
            await asyncio.sleep(time)
            

@client.event
async def on_member_join(member):
    print("New Member")
    await client.send_message(member,"Welcome!")

@client.command(aliases=['dc_link', 'dc'])
async def discord_link(ctx):
    await ctx.channel.send(data["properties"]["discord_link"])

@client.command(aliases=['h'])
async def help(ctx):
    await ctx.channel.send(data)




client.run(TOKEN)
