import discord

from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, CheckFailure
from discord.member import Member

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


intents = discord.Intents.all()
client = commands.Bot(command_prefix='!',help_command=None, intents=discord.Intents.all())



async def status_task():
    messages = data["properties"]["status"]["messages"]
    time = data["properties"]["status"]["time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(name=messages[x]))
            await asyncio.sleep(time)



@client.event
async def on_ready():
    print("Kahlifar: logged in")
    client.loop.create_task(status_task())     


@client.event
async def on_message(message):
    print(message)
    channel = message.channel
    if message.author != client.user:
        if message.content.startswith(PREFIX + "clear"):
            if await check_permissions("clear", message.author, channel):
                args = message.content.split(' ')
                if len(args) == 2:
                    if args[1] == 'all':
                        await channel.purge()
                        await send_deleted_msgs("all", channel)
                    else:
                        try:
                            amount = int(args[1])
                            await channel.purge(limit=amount)
                            await send_deleted_msgs(amount, channel)
                        except TypeError:
                            await send_error("Amount must be a number!", channel)
                        except:
                            await send_error("Please try this format -> `-clear [amount(number)]`", channel)
                elif len(args) == 1:
                    amount = 2
                    await channel.purge(limit=amount)
                    await send_deleted_msgs(amount, channel) 
                else:
                    await send_error("Please try this format -> `-clear [amount(number)]`", channel)
                    return
            else:
                await message.delete()
    await client.process_commands(message)


@client.event
async def on_member_join(member):
    print("New Member")
    await client.send_message(member,"Welcome!")

@client.event
async def check_permissions(command, user:Member, channel):
    command_perm_list = data["properties"]["commands"][str(command)]["permissions"]
    user_allowed = False
    for perm in command_perm_list:
        for role in user.roles:
            if str(perm) == str(role.name):
                user_allowed: bool = True
    if user_allowed == True:
        return True
    else:
        msg = await channel.send("⛔Permission Denied")
        await asyncio.sleep(3)
        await msg.delete()
        return False


@client.event
async def send_error(error, channel):
    msg = await channel.send("⛔Error: %s" % error)
    await asyncio.sleep(5)
    await msg.delete()

@client.event
async def send_deleted_msgs(amount, channel):
    msg = await channel.send("🗑Deleted `%s` messages" % amount)
    await asyncio.sleep(2)
    await msg.delete()

@client.event
async def send_help_embed(ctx):
    help_embed = discord.Embed(title="Hilfe für den <@%s> ." % str(client.user.id),
                                    description="Hier werden dir alle Informationen über die verschiedenen Commands die der <@%s> kann, welche Aliasse er hat und wer die Rechte hat den Command zu benutzen." % str(client.user.id),
                                    colour=discord.Colour(0x9013fe))

    for command in data["properties"]["commands"]:
        
        help_embed.add_field(name=command,
                                value="Beschreibung: %s \n Aliasse: %s \n Rechte: %s hat/haben Zugriff auf diesen Command." % (data["properties"]["commands"][command]["description"], data["properties"]["commands"][command]["aliases"], data["properties"]["commands"][command]["permissions"]))

    await ctx.channel.send(embed=help_embed)



@client.command(aliases=list(data["properties"]["commands"]["help"]["aliases"]))
async def help(ctx):
    # await send_help_embed(ctx)
    await ctx.channel.send("HELP TEST")



@client.command(aliases=list(data["properties"]["commands"]["discord_link"]["aliases"]))
async def discord_link(ctx):
    await ctx.channel.send(data["properties"]["discord_link"])

@client.command(aliases=list(data["properties"]["commands"]["server_ip"]["aliases"]))
async def server_ip(ctx):
    await ctx.channel.send(data["properties"]["server_ip"])

@client.command(aliases=list(data["properties"]["commands"]["social_media"]["aliases"]))
async def social_media(ctx):
    await ctx.channel.send("Social Media Links comming soon")


client.run(TOKEN)