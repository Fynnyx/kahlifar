import discord
from discord.errors import NotFound
from discord.ext import commands, tasks
import discord.utils
from discord.member import Member
import asyncio
import json
import platform

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
intents.guild_messages = True
intents.guild_reactions = True
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

@tasks.loop(seconds=10, count=None)
async def update_json():
    with open("properties.json") as f:
        global data
        data = json.load(f)


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

async def update_embed(message, embed):
    if message:
        await message.edit(embed=embed)

async def get_aliases(command):
    aliases = ""
    for alias in data["properties"]["commands"][command]["aliases"]:
        aliases = aliases + "`" + alias + "`, "
    return aliases

async def get_perms(command):
    perms = ""
    for perm in data["properties"]["commands"][command]["permissions"]:
        perms = perms + "`" + perm + "`, "
    return perms

# On Ready ---------------------------------------------------------------------------

@client.event
async def on_ready():
    status_task.start()
    update_json.start()
    print("Kahlifar: logged in")


# Events ---------------------------------------------------------------------------

@client.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.channels, id=data["properties"]["events"]["on_member_join"]["channel"])
    welcome_message = data["properties"]["events"]["on_member_join"]["message"]
    info_channel = discord.utils.get(member.guild.channels, id=data["properties"]["events"]["on_member_join"]["info_channel"])
    verify_channel = discord.utils.get(member.guild.channels, id=data["properties"]["events"]["on_member_join"]["verify_channel"])
    for role in data["properties"]["events"]["on_member_join"]["roles"]:
        role = discord.utils.get(member.guild.roles, id=int(role))
        await member.add_roles(role)
        print("TEST")
    print("askjd")
    await welcome_channel.send(welcome_message % (str(member.mention), str(verify_channel.id), str(info_channel.id)))


# Error handling ------------------------------------------------------------

# # @client.listen("on_error")
# @client.event
# async def on_error(event, *args, **kwargs):
#     guild = client.get_guild(814230131681132605)
#     await log_to_console("Error in " + event + "\nMore: " + args + "\n\n" + kwargs, guild)

# # @client.listen("on_command_error")
# @client.event
# async def on_command_error(ctx, error):
#     guild = client.get_guild(814230131681132605)
#     await log_to_console(error, guild)


# Help Command ---------------------------------------------------------------------------

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["help"]["aliases"]))
async def help(ctx, user_command=""):
    # print(user_command)

    if user_command == "":
        everyone_perm = "- "
        helper_perm = "- "
        mod_perm = "- "
        owner_perm = "- "

        help_embed = discord.Embed(title="Hilfe für den %s." % str(client.user.name),
                                    description="Hier werden dir alle Rechte über die verschiedenen Commands die der <@%s> hat angezeigt.\n**PREFIX:** %s\nBenutze `%shelp COMMAND` um genauere Details zu erhalten." % (str(client.user.id), PREFIX, PREFIX),
                                    colour=discord.Colour.dark_purple())
        
        for command in data["properties"]["commands"]:
            # print(command)
            if "Everyone" in data["properties"]["commands"][command]["permissions"]:
                everyone_perm = everyone_perm + '`' + command + '`, '
            if "Helper" in data["properties"]["commands"][command]["permissions"]:
                helper_perm = helper_perm + '`' + command + '`, '
            if "Moderator" in data["properties"]["commands"][command]["permissions"]:
                mod_perm = mod_perm + '`' + command + '`, '
            if "Owner" in data["properties"]["commands"][command]["permissions"]:
                owner_perm = owner_perm + '`' + command + '`, '

        help_embed.add_field(name="Everyone:", value=everyone_perm, inline=False)
        help_embed.add_field(name="Helper:", value=helper_perm, inline=False)
        help_embed.add_field(name="Moderator:", value=mod_perm, inline=False)
        help_embed.add_field(name="Owner:", value=owner_perm, inline=False)

        await ctx.channel.send(embed=help_embed)
    else:
        try:
            aliases = await get_aliases(user_command)
            perms = await get_perms(user_command)
            command_help_embed = discord.Embed(title="Help für `" + user_command + "`.", 
                                        description=data["properties"]["commands"][user_command]["description"],
                                        color=discord.Colour.dark_purple())
            command_help_embed.add_field(name="Aliases: ", value=aliases, inline=False)
            command_help_embed.add_field(name="Permissions: ", value=perms, inline=False)
            await ctx.channel.send(embed=command_help_embed)
        except KeyError:
            try:
                alias_exists = False
                for command in data["properties"]["commands"]:
                    if user_command in data["properties"]["commands"][command]["aliases"]:
                        alias_exists = True
                        user_command = command
                if alias_exists == True:
                    aliases = await get_aliases(user_command)
                    perms = await get_perms(user_command)
                    command_help_embed = discord.Embed(title="Help für `" + user_command + "`.", 
                                                description=data["properties"]["commands"][user_command]["description"],
                                                color=discord.Colour.dark_purple())
                    command_help_embed.add_field(name="Aliases: ", value=aliases, inline=False)
                    command_help_embed.add_field(name="Permissions: ", value=perms, inline=False)
                    await ctx.channel.send(embed=command_help_embed)
                else:
                    await send_error("Command `" + user_command + "` nicht gefunden", ctx.channel)
                    await ctx.message.delete()
            except KeyError:
                await send_error("Command `" + user_command + "` nicht gefunden", ctx.channel)
                await ctx.message.delete()
            except:
                await send_error("Frage beim Bot-Admin nach", ctx.channel)
                await ctx.message.delete()

# Embeds ---------------------------------------------------------------------------

@client.command()
async def rules(ctx):
    if await check_permissions("rules", ctx.author, ctx.channel):
        with open("properties.json") as f:
            data = json.load(f)
        await ctx.message.delete()
        krules_embed = await get_embed("rules.json")
        krules_channel = discord.utils.get(ctx.guild.channels, id=data["properties"]["rules"]["channel"])
        try:
            message = await ctx.fetch_message(data["properties"]["rules"]["message"])
            await update_embed(message, krules_embed)
        except NotFound:
            await krules_channel.purge()
            msg = await krules_channel.send(embed=krules_embed)
            data["properties"]["rules"]["message"] = int(msg.id)
            with open("properties.json", 'w') as j:
                j.write(json.dumps(data, indent=2))
    else:
        await ctx.message.delete()

@client.command()
async def krules(ctx):
    if await check_permissions("krules", ctx.author, ctx.channel):
        with open("properties.json") as f:
            data = json.load(f)
        await ctx.message.delete()
        krules_embed = await get_embed("k-rules.json")
        krules_channel = discord.utils.get(ctx.guild.channels, id=data["properties"]["krules"]["channel"])
        try:
            message = await ctx.fetch_message(data["properties"]["krules"]["message"])
            await update_embed(message, krules_embed)
        except NotFound:
            await krules_channel.purge()
            msg = await krules_channel.send(embed=krules_embed)
            data["properties"]["krules"]["message"] = int(msg.id)
            with open("properties.json", 'w') as j:
                j.write(json.dumps(data, indent=2))
    else:
        await ctx.message.delete()

@client.command()
async def faq(ctx):
    if await check_permissions("faq", ctx.author, ctx.channel):
        with open("properties.json") as f:
            data = json.load(f)
        await ctx.message.delete()
        channel = discord.utils.get(ctx.guild.channels, id=data["properties"]["faq"]["channel"])
        embed = await get_embed("faq.json")
        try:
            message = await ctx.fetch_message(data["properties"]["faq"]["message"])
            await update_embed(message, embed)
        except NotFound:
            await channel.purge()
            msg = await channel.send(embed=embed)
            data["properties"]["faq"]["message"] = int(msg.id)
            with open("properties.json", 'w') as j:
                j.write(json.dumps(data, indent=2))
            

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


# Commands ---------------------------------------------------------------------------

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["discord_link"]["aliases"]))
async def discord_link(ctx):
    await ctx.channel.send(data["properties"]["discord_link"])

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["server_ip"]["aliases"]))
async def server_ip(ctx):
    await ctx.channel.send(data["properties"]["server_ip"])

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["social_media"]["aliases"]))
async def social_media(ctx):
    sm_embed = await get_embed("social_media.json")
    await ctx.channel.send(embed=sm_embed)

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["author"]["aliases"]))
async def author(ctx):
    await ctx.channel.send("Freut mich dass du dich für die Herkunft des Bots interessierst.\n\nDieser Bot ist von Fynnyx gecoded.\nMöchtest du den Code des Bots sehen? Dann findest du alles unter diesem Link (https://github.com/Fynnyx/kahlifar).\nAusserdem kannst du gerne mit Fynnyx darüber reden.")

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["github"]["aliases"]))
async def github(ctx):
    await ctx.channel.send("**GitHub: **https://github.com/Fynnyx/kahlifar")

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["pcstats"]["aliases"]))
async def pcstats(ctx):
    stats_embed = discord.Embed(title="Stats vom Server auf dem der Bot läuft", description="Für genauere Details frage Fynnyx der hilft dir gerne.", colour=discord.Colour.dark_purple())
    stats_embed.add_field(name="System:", value=str(platform.system() + " " + platform.release()), inline=False)
    stats_embed.add_field(name="System Version:", value=platform.version(), inline=False)
    stats_embed.add_field(name="Network:", value=platform.node(), inline=False)
    stats_embed.add_field(name="Processor:", value=platform.processor(), inline=False)
    stats_embed.add_field(name="Python version:", value=platform.python_version(), inline=False)
    await ctx.channel.send(embed=stats_embed)


client.run(TOKEN)