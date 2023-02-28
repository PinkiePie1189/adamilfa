import discord
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
from os import environ
import yt_dlp
import asyncio

bot = discord.Bot()

# we need to limit the guilds for testing purposes
# so other users wouldn't see the command that we're testing

voice = None
play_queue = []

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

@bot.command(description="Connect to voice")
async def connect(ctx):
    channel = ctx.author.voice.channel
    voice = await channel.connect()
    await ctx.respond(f"M-am conectat pe voice")
    return voice


async def play_next(ctx, err):
    global play_queue
    if err:
        print(err)
    else:
        if len(play_queue) > 0:
            await play_song(ctx)
        

async def play_song(ctx):
    global voice, play_queue, bot
    if len(play_queue) > 0:
        video = play_queue[0]

        print(video['title'])

        play_queue = play_queue[1::]

        url = video["formats"][4]["url"]
        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice.play(FFmpegPCMAudio(url, **FFMPEG_OPTS), after=lambda err: bot.loop.create_task(play_next(ctx, err)))

        await ctx.send(f"Now playing {video['title']}")

        


@bot.command(description="Play some jams")
async def play(ctx, url_arg : discord.Option(str)):
    global voice
    global play_queue

    if not voice:
        voice = await connect(ctx)

    
    ydl_opts = {'default_search': 'ytsearch'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
       
        info = ydl.extract_info(url_arg, download=False)


        if "entries" in info:
            video = info["entries"][0]
        else:
            video = info

        play_queue.append(video)
        await ctx.respond(f"Added {video['title']} to the play queue")

    if not voice.is_playing():
        await play_song(ctx)
        
@bot.command(description="Show the play queue")
async def queue(ctx):
    global play_queue

    queue_elems = ''
    for idx, video in enumerate(play_queue):
        queue_elems += f"{idx}.) **{video['title']}**\n"

    await ctx.respond(queue_elems)  

if __name__ == '__main__':
    load_dotenv()
    bot.run(environ['API_TOKEN'])