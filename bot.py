import discord
from discord.ext import commands
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {
    'format': 'bestaudio',
    'noplaylist': True
}

FFMPEG_OPTIONS = {
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Debes estar en un canal de voz")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.invoke(join)

    vc = ctx.voice_client

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']

    source = await discord.FFmpegOpusAudio.from_probe(url2)

    vc.stop()
    vc.play(source)

    await ctx.send(f"Reproduciendo: {info['title']}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))