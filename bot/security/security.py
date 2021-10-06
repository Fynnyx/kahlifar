import discord
from discord import Member
from discord import channel
from discord.ext import commands
import discord.utils
import asyncio
import json

with open("properties.json", encoding="UTF-8") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]
PREFIX = data["properties"]["prefix"]

intents = discord.Intents()
intents.guilds = True
intents.members = True
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.dm_messages = True

client = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents)


# Tasks ---------------------------------------------------------------------------




# Functions ---------------------------------------------------------------------------

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


async def sync_member(member):
    gen_guild = discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
    gen_member = discord.utils.get(gen_guild.members, id=member.id)
    roles = gen_member.roles
    display_name = gen_member.display_name

    if await is_verified(member, gen_member):
        await member.edit(nick=display_name)



async def is_verified(game_member, gen_member):
    game_guild = discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
    for role in gen_member.roles:
        if discord.utils.get(gen_member.guild.roles, name=role):
            game_role = discord.utils.get(game_guild)
            game_member.add_roles()


# Events    ----------------------------------------------------------------------------

@client.event
async def on_member_join(member):
    if int(member.guild.id) == data["properties"]["general"]["guild_id"]:
        server = "general"
    elif int(member.guild.id) == data["properties"]["gaming"]["guild_id"]:
        server = "gaming"
    welcome_channel = await client.fetch_channel(data["properties"][server]["events"]["on_member_join"]["channel"])
    welcome_message = data["properties"][server]["events"]["on_member_join"]["message"]
    info_channel = await client.fetch_channel(data["properties"][server]["events"]["on_member_join"]["info_channel"])
    basic_member_role = discord.utils.get(member.guild.roles, id=int(data["properties"][server]["events"]["on_member_join"]["role_id"]))
    await member.add_roles(basic_member_role)
    await welcome_channel.send(welcome_message % (str(member.mention), str(info_channel.id)))

@client.event
async def on_reaction_add(reaction, user):
    if reaction == "asd":
        print("verify")


# On Ready  ----------------------------------------------------------------------------

@client.event
async def on_ready():
    print("%sKahlifar Security: logged in" % PREFIX)
    await send_verify()

async def send_verify():
    for guild in client.guilds:
        if int(guild.id) == data["properties"]["general"]["guild_id"]:
            server = "general"
        elif int(guild.id) == data["properties"]["gaming"]["guild_id"]:
            server = "gaming"
        verify_channel = discord.utils.get(guild.channels, id=data["properties"][server]["events"]["on_reaction_add"]["verify"]["channel"])
        verify_emoji = data["properties"][server]["events"]["on_reaction_add"]["verify"]["emoji"]
        verify_message = data["properties"][server]["events"]["on_reaction_add"]["verify"]["message"]
        await verify_channel.purge()
        msg = await verify_channel.send(verify_message % (verify_emoji))
        await msg.add_reaction(verify_emoji)
        data["properties"][server]["events"]["on_reaction_add"]["verify"]["message_id"] = int(msg.id)
        with open("properties.json", "w", encoding="UTF-8") as f:
            f.write(json.dumps(data, indent=2))



# Commands  ----------------------------------------------------------------------------

@client.command(aliases=data["properties"]["commands"]["clear"]["aliases"])
async def clear(ctx, amount:str):
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
    else:
        await send_error("Please try this format -> `-clear [amount(number)]`", channel)
        return

async def send_deleted_msgs(amount, channel):
    msg = await channel.send("🗑Deleted `%s` messages" % amount)
    await asyncio.sleep(2)
    await msg.delete()


@client.command()
async def test(ctx):
    await sync_member(ctx.author)
    print("Test Command Triggered")


client.run(TOKEN)