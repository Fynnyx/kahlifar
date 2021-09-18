import discord
import discord.utils
from discord.ext import commands
import asyncio
import youtube_dl
import os
import json

with open("properties.json") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]
PREFIX = data["properties"]["prefix"]

client = commands.Bot(command_prefix=PREFIX, help_command=None, intents=discord.Intents.all())


# Functions ---------------------------------------------------------------------------

async def status_task():
    messages = data["properties"]["messages"]
    time = data["properties"]["status_time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(name=messages[x]))
            await asyncio.sleep(time)

# On Ready ---------------------------------------------------------------------------

@client.event
async def on_ready():
    print(".Musicbot: logged in")
    client.loop.create_task(status_task())


# Commands ---------------------------------------------------------------------------

@client.command()
async def join(ctx):
    if (ctx.author.voice):
        vc = ctx.message.author.voice.channel
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if not voice:
            await vc.connect()
        else:
            await ctx.channel.send("Sorry, but im already in use!")
    else:
        await ctx.channel.send("You must be in voice channel!")


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        await voice.disconnect()
    else:
        await ctx.channel.send("I'm not in a voice channel!")
    

@client.command()
async def play(ctx, url:str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return

    try:
        if (ctx.author.voice):
            vc = ctx.message.author.voice.channel
            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
            if not voice:
                await vc.connect()

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, "song.mp3")
                if voice:
                    voice.play(discord.FFmpegPCMAudio("song.mp3"))
                else:
                    await ctx.channel.send("Something went wrong")
            else:
                await ctx.channel.send("Sorry, but im already in use!")
        else:
            await ctx.channel.send("You must be in voice channel!")
    except discord.ext.commands.errors.MissingRequiredArgument:
        await ctx.channel.send("Schreibe bitte mit einer URL")

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        await voice.pause()
    else:
        await ctx.channel.send("Currently no audo is playing!")

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.channel.send("No audio paused")

@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        voice.stop()
    else:
        await ctx.channel.send("I'm not in a voice channel!")

client.run(TOKEN)

