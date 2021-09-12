from asyncio.protocols import DatagramProtocol
import discord
from discord import embeds
from discord import channel
from discord import message

from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, CheckFailure

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



client = commands.Bot(command_prefix=PREFIX, help_command=None)



async def status_task():
    messages = data["properties"]["status"]["messages"]
    time = data["properties"]["status"]["time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(messages[x]), status=discord.Status.online)
            await asyncio.sleep(time)



@client.event
async def on_ready():
    print("Kahlifar: logged in")
    client.loop.create_task(status_task())            

# @client.event
# async def on_member_join(member):
#     print("New Member")
#     await client.send_message(member,"Welcome!")


@client.event
async def send_error(ctx, error, channel):
    await ctx,channel.send("⛔Error: %s" % error)



@client.command(aliases=list(data["properties"]["commands"]["help"]["aliases"]))
async def help(ctx):
    await ctx.channel.send("Command information comming soon")


@client.command(aliases=list(data["properties"]["commands"]["discord_link"]["aliases"]))
async def discord_link(ctx):
    await ctx.channel.send(data["properties"]["discord_link"])

@client.command(aliases=list(data["properties"]["commands"]["server_ip"]["aliases"]))
async def server_ip(ctx):
    await ctx.channel.send(data["properties"]["server_ip"])

@client.command(aliases=list(data["properties"]["commands"]["social_media"]["aliases"]))
async def social_media(ctx):
    await ctx.channel.send("Social Media Links comming soon")


@client.command()
@has_permissions(manage_messages=True)
async def clear(ctx):
    args = message.content.split(' ')
    print(args)
    if len(args) == 2:
        amount = args[2]
        await ctx.channel.purge(limit=amount)
        await ctx.channel.send("Deleted %s messaged" % amount) 
    elif len(args) == 1:
        amount = 1
        await ctx.channel.purge(limit=amount)
        await ctx.channel.send("Deleted %s messaged" % amount) 
    else:
        await send_error("Please try this format -> ´-clear [amount]´")
        return

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send_message(ctx.message.channel, text)


client.run(TOKEN)
