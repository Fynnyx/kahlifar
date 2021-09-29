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
    print(PREFIX + "Musicbot: logged in")

    global queue
    queue = []
    global current_song
    current_song = ''
    global ydl_opts
    ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

    client.loop.create_task(status_task())

# Events ---------------------------------------------------------------------------

@client.event
async def voice_handler(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        while voice.is_playing() == False and voice.is_connected() == True and queue != []:
            await play_audio(ctx)

@client.event
async def play_audio(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        if voice.is_playing():
            return
        else:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([queue[0]])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "./song.mp3")
            voice.play(discord.FFmpegPCMAudio("./song.mp3"))
            current_song = str(queue[0])
            await ctx.channel.send(current_song)
            queue.pop(0)
            print(queue)



# Commands ---------------------------------------------------------------------------

@client.command()
async def join(ctx):
    if (ctx.author.voice):
        vc = ctx.message.author.voice.channel
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if not voice:
            await vc.connect()

            client.loop.create_task(voice_handler(ctx))
            
            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
            voice.stop()
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
        queue.append(url)
        print(queue)
        await ctx.send("Queued the song \n Wait for the current playing music to end or use the 'stop' command")
        return

    try:
        if (ctx.author.voice):
            vc = ctx.message.author.voice.channel
            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
            if not voice:
                await vc.connect()

                client.loop.create_task(voice_handler(ctx))

                voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
                voice.stop()
                voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
                if voice:
                    queue.append(url)
                    print(queue)
                    await play_audio(ctx)
                else:
                    await ctx.channel.send("Something went wrong")
            else:
                queue.append(url)
                print(queue)
        else:
            await ctx.channel.send("You must be in voice channel!")
    except discord.ext.commands.errors.MissingRequiredArgument:
        await ctx.channel.send("Schreibe bitte mit einer URL")

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
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

@client.command()
async def queue(ctx):
    await ctx.channel.send('Now playing: ' + current_song)


@client.command()
async def status(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        print("Bot connected")
        if voice.is_paused():
            print("Bot paused")
        if voice.is_playing():
            print("Bot playing")
    else:
        print("not connected")


client.run(TOKEN)

