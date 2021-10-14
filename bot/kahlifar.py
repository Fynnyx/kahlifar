import discord
from discord.ext import commands, tasks
import discord.utils
from discord.member import Member
import asyncio
import json

from log import log_to_console


with open("properties.json") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]
PREFIX = data["properties"]["prefix"]

discord_link = data["properties"]["discord_link"]
server_ip = data["properties"]["server_ip"]

intents = discord.Intents()
intents.bans = False
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

@tasks.loop(count=None)
async def status_task():
    messages = data["properties"]["status"]["messages"]
    time = data["properties"]["status"]["time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(name=messages[x]))
            await asyncio.sleep(time)


# Functions ---------------------------------------------------------------------------

async def get_embed(file:str):
    with open("./assets/embeds/%s" % file, encoding="UTF-8") as e:
        edata = json.load(e)

    embed = discord.Embed(title=edata["embed"]["title"],
                            description=edata["embed"]["description"],
                            colour=discord.Colour(edata["embed"]["color"]))

    for field in edata["embed"]["fields"]:
        embed.add_field(name=field["name"], value=field["value"], inline=False)
    return embed


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
    status_task.start()
    print("Kahlifar: logged in")


# Events ---------------------------------------------------------------------------

@client.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.channels, id=data["properties"]["events"]["on_member_join"]["channel"])
    welcome_message = data["properties"]["events"]["on_member_join"]["message"]
    info_channel = discord.utils.get(member.guild.channels, id=data["properties"]["events"]["on_member_join"]["info_channel"])
    verify_channel = discord.utils.get(member.guild.channels, id=data["properties"]["events"]["on_member_join"]["verify_channel"])
    basic_member_role = discord.utils.get(member.guild.roles, id=int(data["properties"]["events"]["on_member_join"]["role_id"]))
    await member.add_roles(basic_member_role)
    await welcome_channel.send(welcome_message % (str(member.mention), str(verify_channel.id), str(info_channel.id)))


# Error handling ------------------------------------------------------------

# @client.listen("on_error")
async def log_error(error):
    guild = client.get_guild(814230131681132605)
    await log_to_console(error, guild)

# @client.listen("on_command_error")
async def log_command_error(ctx, error):
    guild = client.get_guild(814230131681132605)
    await log_to_console(error, guild)


# Help Command ---------------------------------------------------------------------------

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["help"]["aliases"]))
async def help(ctx):
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


# Embeds ---------------------------------------------------------------------------

@client.command()
async def rules(ctx):
    if await check_permissions("rules", ctx.author, ctx.channel):
        rule_embed = await get_embed("rules.json")
        rule_channel = discord.utils.get(ctx.guild.channels, id=data["properties"]["rule"]["channel"])
        await rule_channel.purge()
        await rule_channel.send(embed=rule_embed)
    await ctx.message.delete()

@client.command()
async def krules(ctx):
    if await check_permissions("krules", ctx.author, ctx.channel):
        krules_embed = await get_embed("k-rules.json")
        krules_channel = discord.utils.get(ctx.guild.channels, id=data["properties"]["krules"]["channel"])
        await krules_channel.purge()
        await krules_channel.send(embed=krules_embed)
    await ctx.message.delete()

@client.command()
async def infos(ctx):
    if await check_permissions("infos", ctx.author, ctx.channel):
        await ctx.message.delete()
        with open("./assets/infos.json", encoding="UTF-8") as j:
            info = json.load(j)
        image_path = "./assets/images/"
        channel = ctx.channel
        await channel.purge()

        await channel.send(file=discord.File(image_path+info["infos"]["file1"]))
        await channel.send(info["infos"]["text1"] % (751097780004585483, 451776092785737728))
        await channel.send(file=discord.File(image_path+info["infos"]["file2"]))
        await channel.send(info["infos"]["text2"] % (835629559645995009, 838380050952486922, 835631187094667315, 863764198664175646, 896498793711812659, 815849652632027167, 836696030732877897, 836696294869041212))
        await channel.send(file=discord.File(image_path+info["infos"]["file3"]))
        await channel.send(info["infos"]["text3"] % (814231323224572006, 814234539773001778, 834483454968070164, 814523816818638868, 895288280269094983, 842867716523294741, 897781560038793226))
    
    else:
        await ctx.message.delete()


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

    await ctx.channel.send(embed=sm_embed)


client.run(TOKEN)