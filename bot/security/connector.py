import discord
from discord import Member
from discord.ext import commands
import discord.utils
import asyncio
import json

from log import log_to_console


with open("properties.json", encoding="UTF-8") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]
PREFIX = data["properties"]["prefix"]

intents = discord.Intents()
intents.bans = True
intents.dm_messages = True
intents.dm_reactions= False
intents.dm_typing= False
intents.emojis = True
intents.guild_messages = False
intents.guild_reactions = False
intents.guild_typing = False
intents.guilds = True
intents.integrations = False
intents.invites = True
intents.members = True
intents.messages = True
intents.presences= False
intents.reactions = True
intents.typing= False
intents.voice_states= False
intents.webhooks= False

client = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents)


# Tasks ---------------------------------------------------------------------------

async def status_task():
    messages = data["properties"]["status"]["messages"]
    time = data["properties"]["status"]["time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(name=messages[x]))
            await asyncio.sleep(time)


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

async def verify_user(user):
    if int(user.guild.id) == data["properties"]["general"]["guild_id"]:
        server = "general"
    role = discord.utils.get(user.guild.roles, id=data["properties"][server]["events"]["on_reaction_add"]["verify"]["role"])
    rm_role = discord.utils.get(user.guild.roles, id=data["properties"][server]["events"]["on_member_join"]["role_id"])
    await user.add_roles(role)
    await user.remove_roles(rm_role)

async def sync_member(member):
    gen_guild = discord.utils.get(client.guilds, id=data["properties"]["general"]["guild_id"])
    gen_member = discord.utils.get(gen_guild.members, id=member.id)
    if gen_member != None:
        if await is_verified(member, gen_member):
            await sync_nick(member.id, gen_member.display_name)
            await sync_roles(member, gen_member)
        else:
            await member.send(data["properties"]["general"]["events"]["sync_member"]["nv_message"] % (data["properties"]["general"]["infinite_invite"]))
    else:
        await member.send(data["properties"]["general"]["events"]["sync_member"]["nv_message"] % (data["properties"]["general"]["infinite_invite"]))


async def is_verified(game_member, gen_member):
    for role in gen_member.roles:
        if role.id == data["properties"]["general"]["events"]["on_reaction_add"]["verify"]["role"]:
            return True

async def sync_nick(member_id, nick):
    gen_guild = discord.utils.get(client.guilds, id=data["properties"]["general"]["guild_id"])
    game_guild = discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
    gen_user = discord.utils.get(gen_guild.members, id=member_id)
    game_user = discord.utils.get(game_guild.members, id=member_id)
    try:
        await gen_user.edit(nick=nick)
        await game_user.edit(nick=nick)
    except discord.errors.Forbidden:
        return

async def sync_roles(member, gen_member):
    await member.remove_roles()
    for role in gen_member.roles:
        if discord.utils.get(member.guild.roles, name=role.name) and str(role.name) != "@everyone":
            game_role = discord.utils.get(member.guild.roles, name=role.name)
            await member.add_roles(game_role)

async def sync_user_roles(member_id, guild):
    if guild.id == data["properties"]["general"]["guild_id"]:
        gen_guild = guild
        game_guild = discord.utils.get(client.guilds, id=(data["properties"]["gaming"]["guild_id"]))
        game_user = discord.utils.get(game_guild.members, id=member_id)
        gen_user = discord.utils.get(gen_guild.members, id=member_id)
        if game_user != None:
            await game_user.remove_roles()
            for role in gen_user.roles:
                if discord.utils.get(game_guild.roles, name=role.name) and str(role.name) != "@everyone":
                    game_role = discord.utils.get(game_guild.roles, name=role.name)
                    await game_user.add_roles(game_role)


# Listerners    ----------------------------------------------------------------------------

@client.event
async def on_member_join(member):
    game_guild = discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
    game_member = discord.utils.get(game_guild.members, id=member.id)
    print(game_member)
    if game_member != None:
        await sync_member(member)

@client.event
async def on_member_remove(member):
    if member.guild.id == data["properties"]["general"]["guild_id"]:
        game_guild =  discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
        game_member = discord.utils.get(game_guild.members, id=member.id)
        if game_member != None:
            await game_member.kick()

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.guild.id == data["properties"]["general"]["guild_id"]:
        server = "general"
    elif reaction.message.guild.id == data["properties"]["gaming"]["guild_id"]:
        server = "gaming"
    # VERIFY
    if reaction.emoji == data["properties"][server]["events"]["on_reaction_add"]["verify"]["emoji"] and not user.bot:
        await verify_user(user)

@client.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        # print(before.roles)
        # print(after.roles)
        await sync_user_roles(after.id, after.guild)
    if before.nick != after.nick:
        await sync_nick(after.id, after.nick)

@client.event
async def on_guild_role_create(role):
    if role.guild.id == data["properties"]["general"]["guild_id"]:
        guild = discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
    elif role.guild.id == data["properties"]["gaming"]["guild_id"]:
        guild = discord.utils.get(client.guilds, id=data["properties"]["general"]["guild_id"])
    if discord.utils.get(guild.roles, name=role.name) == None:
        await guild.create_role(name=role.name, permissions=role.permissions, colour=role.colour, hoist=role.hoist, mentionable=role.mentionable)

@client.event
async def on_guild_role_delete(role):
    if role.guild.id == data["properties"]["general"]["guild_id"]:
        guild = discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
    elif role.guild.id == data["properties"]["gaming"]["guild_id"]:
        guild = discord.utils.get(client.guilds, id=data["properties"]["general"]["guild_id"])
    if discord.utils.get(guild.roles, name=role.name) != None:
        other_role = discord.utils.get(guild.roles, name=role.name)
        await other_role.delete()

@client.event
async def on_guild_role_update(before, after):
    if after.guild.id == data["properties"]["general"]["guild_id"]:
        guild = discord.utils.get(client.guilds, id=data["properties"]["gaming"]["guild_id"])
    elif after.guild.id == data["properties"]["gaming"]["guild_id"]:
        guild = discord.utils.get(client.guilds, id=data["properties"]["general"]["guild_id"])
    if discord.utils.get(guild.roles, name=before.name) != None:
        other_role = discord.utils.get(guild.roles, name=before.name)
        # if after.name != other_role.name or after.colour != other_role.colour or after.permissions != other_role.permissions or after.hoist != other_role.hoist or after.mentionable != other_role.mentionable or after.position != other_role.position:
        #     await other_role.edit(name=after.name, permissions=after.permissions, colour=after.colour, hoist=after.hoist, mentionable=after.mentionable, position=after.position)
        if after.name != other_role.name or after.colour != other_role.colour or after.permissions != other_role.permissions or after.hoist != other_role.hoist or after.mentionable != other_role.mentionable:
            await other_role.edit(name=after.name, permissions=after.permissions, colour=after.colour, hoist=after.hoist, mentionable=after.mentionable)
    # await guild.create_role(name=after.name, permissions=after.permissions, colour=after.colour, hoist=after.hoist, mentionable=after.mentionable)

# MOD LOG
@client.event
async def on_message_delete(message):
    print("lol")
# message edit
# member update
# member ban
# member kick
# member unban
# role create
# role delete
# role update



# Error handling ------------------------------------------------------------

# @client.listen("on_error")
@client.event
async def on_error(event, *args, **kwargs):
    guild = client.get_guild(814230131681132605)
    await log_to_console("Error in " + event + "\nMore: " + args + "\n\n" + kwargs, guild)

# @client.listen("on_command_error")
@client.event
async def on_command_error(ctx, error):
    guild = client.get_guild(814230131681132605)
    await log_to_console(error, guild)

# On Ready  ----------------------------------------------------------------------------

@client.event
async def on_ready():
    print("%sKahlifar Security: logged in" % PREFIX)
    client.loop.create_task(status_task())
    await send_verify()

async def send_verify():
    guild = discord.utils.get(client.guilds, id=data["properties"]["general"]["guild_id"])
    server = "general"
    verify_channel = discord.utils.get(guild.channels, id=895385320848236574)
    verify_emoji = data["properties"][server]["events"]["on_reaction_add"]["verify"]["emoji"]
    verify_message = data["properties"][server]["events"]["on_reaction_add"]["verify"]["message"]
    await verify_channel.purge()
    msg = await verify_channel.send(verify_message % (verify_emoji))
    await msg.add_reaction(verify_emoji)
    data["properties"][server]["events"]["on_reaction_add"]["verify"]["message_id"] = int(msg.id)
    with open("properties.json", "w", encoding="UTF-8") as f:
        f.write(json.dumps(data, indent=2))
    print("%sKahlifar Security: verify message sent" % PREFIX)


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
async def sync(ctx):
    await sync_member(ctx.author)


client.run(TOKEN)