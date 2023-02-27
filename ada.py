import discord
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
from os import environ
import yt_dlp

bot = discord.Bot()

# we need to limit the guilds for testing purposes
# so other users wouldn't see the command that we're testing

voice = None

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

@bot.command(description="Connect to voice")
async def connect(ctx):
    channel = ctx.author.voice.channel
    voice = await channel.connect()
    await ctx.respond(f"M-am conectat pe voice")
    return voice

@bot.command(description="Play some jams")
async def play(ctx, url_arg : discord.Option(str)):
    global voice
    if not voice:
        voice = await connect(ctx)

    

    ydl_opts = {'default_search': 'ytsearch'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
       
        info = ydl.extract_info(url_arg, download=False)


        if "entries" in info:
            video = info["entries"][0]
        else:
            video = info

        url = video["formats"][4]["url"]

        if voice.is_playing():
            voice.stop()


        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        voice.play(FFmpegPCMAudio(url, **FFMPEG_OPTS))

        await ctx.respond(f"Now playing {video['title']}")







if __name__ == '__main__':
    load_dotenv()
    bot.run(environ['API_TOKEN'])