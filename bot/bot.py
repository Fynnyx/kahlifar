from os import name
import re
import discord
from discord import FFmpegPCMAudio

from discord.ext.commands.core import check
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, CheckFailure


import discord.utils

from discord_buttons_plugin import ButtonsClient, ActionRow
from discord_components import *
from discord.member import Member

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

import asyncio
import json



with open("properties.json") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]
PREFIX = data["properties"]["prefix"]

discord_link = data["properties"]["discord_link"]
server_ip = data["properties"]["server_ip"]


client = commands.Bot(command_prefix=PREFIX, help_command=None, intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
button = ButtonsClient(client)


# Functions ---------------------------------------------------------------------------

async def status_task():
    messages = data["properties"]["status"]["messages"]
    time = data["properties"]["status"]["time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(name=messages[x]))
            await asyncio.sleep(time)


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

async def send_error(error, channel):
    msg = await channel.send("⛔Error: %s" % error)
    await asyncio.sleep(5)
    await msg.delete()


# On Ready ---------------------------------------------------------------------------

@client.event
async def on_ready():
    print("Kahlifar: logged in")
    client.loop.create_task(status_task())
    # await client.change_presence(discord.CustomActivity(name="Test", type=discord.ActivityType.streaming))


# Moderator ---------------------------------------------------------------------------

@slash.slash(
    name="clear",
    description="Clear Messages", 
    guild_ids=[804436188433088574],
    options=[
        create_option(
            name="amount",
            description="How many Messages",
            option_type=3,
            required=False
        )
    ]
)    
@client.command(aliases=data["properties"]["commands"]["clear"]["aliases"])
async def clear(ctx:SlashContext, amount:str):
    channel = ctx.message.channel
    if await check_permissions("clear", ctx.message.author, channel):
        if amount == 'all':
            await channel.purge()
            await send_deleted_msgs("all", channel)
        elif amount:
            try:
                amount = int(amount)
                await channel.purge(limit=amount)
                await send_deleted_msgs(amount, channel)
            except TypeError:
                await send_error("Amount must be a number!", channel)
            except:
                await send_error("Please try this format -> `-clear [amount(number)]`", channel)
    elif isinstance(amount, commands.MissingRequiredArgument):
        amount = 2
        await channel.purge(limit=amount)
        await send_deleted_msgs(amount, channel) 
    else:
        await send_error("Please try this format -> `-clear [amount(number)]`", channel)
        return


async def send_deleted_msgs(amount, channel):
    msg = await channel.send("🗑Deleted `%s` messages" % amount)
    await asyncio.sleep(2)
    await msg.delete()



# @client.event
# async def on_member_join(member):
#     print("New Member")
#     await client.send_message(member,"Welcome!")


# Help Command ---------------------------------------------------------------------------

@slash.slash(
    name="help", 
    description="Gives you all commands.", 
    guild_ids=[804436188433088574])
@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["help"]["aliases"]))
async def help(ctx:SlashContext):
    await send_help_embed(ctx)

async def send_help_embed(ctx):
    help_embed = discord.Embed(title="Hilfe für den %s." % str(client.user.name),
                                    description="Hier werden dir alle Informationen über die verschiedenen Commands die der <@%s> kann, welche Aliasse er hat und wer die Rechte hat den Command zu benutzen." % str(client.user.id),
                                    colour=discord.Colour(0x9013fe))

    for command in data["properties"]["commands"]:
        
        help_embed.add_field(name="-- %s --" %(command),
                                value="*Beschreibung:* %s \n *Aliasse:* %s \n *Rechte:* %s hat/haben Zugriff auf diesen Command." % (data["properties"]["commands"][command]["description"], data["properties"]["commands"][command]["aliases"], data["properties"]["commands"][command]["permissions"]),
                                inline=bool(data["properties"]["commands"][command]["inline"]))

    await ctx.channel.send(embed=help_embed)


# Voice Channel ---------------------------------------------------------------------------

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["join"]["aliases"]))
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        global voice
        voice = await channel.connect()
        # source = FFmpegPCMAudio("./assets/sounds/airhorn_sound.mp3")
        # player = voice.play(source)
    else:
        await send_error("You have to connect to a Voice-Channel", ctx.message.channel)
        await asyncio.sleep(3)
        await ctx.message.delete()

@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.channel.send("💨 Successfully disconnected!")
    else:
        await send_error("Ich bin in keinem Voice Channel", ctx.message.channel)
        await asyncio.sleep(3)
        await ctx.message.delete()

@client.command(pass_context=True)
async def buzzer(ctx):
    if ctx.voice_client:
        source = FFmpegPCMAudio("./assets/sounds/airhorn_sound.mp3")
        player = voice.play(source)
@client.command(pass_context=True)
async def cbuzzer(ctx):
    if voice:
        source = FFmpegPCMAudio("./assets/sounds/mlg-airhorn.mp3")
        player = voice.play(source)

@client.command(aliases=list(data["properties"]["commands"]["sound_board"]["aliases"]))
async def sound_board(ctx):
    sb_embed = discord.Embed(title="🔊-Kahlifar-Soundboard-🔊", 
                                colour=discord.Colour(0x9013fe), 
                                description="Hier kannst du mit dem Bot verschiedenste Sounds in einem VC spielen.\n Hab spass")

    sb_embed.set_footer(text="❗-Abuse führt zu einem Bann")
    
    sb_embed.add_field(name="1️⃣", value="Normal Airhorn sound", inline=True)
    sb_embed.add_field(name="2️⃣", value="MLG Airhorn", inline=True)
    sb_embed.add_field(name="3️⃣", value="Discord Join Sound", inline=True)
    sb_embed.add_field(name="4️⃣", value="Discord Left Sound", inline=True)
    sb_embed.add_field(name="5️⃣", value="-", inline=True)
    sb_embed.add_field(name="6️⃣", value="-", inline=True)

    await ctx.send(embed=sb_embed, 
                    components=[
                            Button(
                                emoji="1️⃣", 
                                custom_id="button1",
                                style=ButtonStyle(value=1)),
                            Button(
                                emoji="2️⃣",
                                custom_id="button2",
                                style=ButtonStyle(value=1)),
                            Button(
                                emoji="3️⃣",
                                custom_id="button3",
                                style=ButtonStyle(value=1)),
                            Button(
                                emoji="4️⃣",
                                custom_id="button4",
                                style=ButtonStyle(value=1))
                            ])
    interaction = await client.wait_for("button_click", check=lambda i: i.component.label.startswith("1️⃣"))
    await interaction(await play_sound("./assets/sounds/airhorn_sound.mp3"))
                        
# @button.click
# async def button1(ctx):
#     await play_sound("./assets/sounds/airhorn_sound.mp3")

@button.click
async def button2(ctx):
    await play_sound("./assets/sounds/mlg-airhorn.mp3")

@button.click
async def button3(ctx):
    await play_sound("./assets/sounds/discord_join.mp3")
@button.click
async def button4(ctx):
    await play_sound("./assets/sounds/discord_leave.mp3")

async def play_sound(pfad:str):
    source = FFmpegPCMAudio(pfad)
    player = voice.play(source)

        

# Social Media ---------------------------------------------------------------------------

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["discord_link"]["aliases"]))
async def discord_link(ctx):
    await ctx.channel.send(data["properties"]["discord_link"])

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["server_ip"]["aliases"]))
async def server_ip(ctx):
    await ctx.channel.send(data["properties"]["server_ip"])

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["social_media"]["aliases"]))
async def social_media(ctx):
    sm_embed = discord.Embed(title="Social Media Links für Kahlifar",
                                    description="Hier werden dir alle Informationen über die verschiedenen Commands die der <@%s> kann, welche Aliasse er hat und wer die Rechte hat den Command zu benutzen." % str(client.user.id),
                                    colour=discord.Colour(0x9013fe))

    for command in data["properties"]["commands"]:
        
        sm_embed.add_field(name="-- %s --" %(command),
                                value="*Beschreibung:* %s \n *Aliasse:* %s \n *Rechte:* %s hat/haben Zugriff auf diesen Command." % (data["properties"]["commands"][command]["description"], data["properties"]["commands"][command]["aliases"], data["properties"]["commands"][command]["permissions"]),
                                inline=bool(data["properties"]["commands"][command]["inline"]))

    await ctx.channel.send(embed=sm_embed)







client.run(TOKEN)