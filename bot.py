import discord
from discord.ext import commands
import yt_dlp
import os
import shutil
import subprocess
import glob
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Buscar FFmpeg en múltiples ubicaciones
def find_ffmpeg():
    # Primero intentar con shutil.which
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    
    # Buscar en /nix/store (Railway/Nixpacks)
    try:
        nix_paths = glob.glob("/nix/store/*/bin/ffmpeg")
        if nix_paths:
            return nix_paths[0]
    except:
        pass
    
    # Rutas comunes
    possible_paths = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "-version"], 
                                   capture_output=True, 
                                   timeout=5)
            if result.returncode == 0:
                return path
        except:
            continue
    
    return "ffmpeg"  # Fallback por defecto

FFMPEG_PATH = find_ffmpeg()

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    print(f'FFmpeg encontrado en: {FFMPEG_PATH}')
    
    # Mostrar todos los FFmpeg disponibles en /nix/store
    try:
        nix_ffmpegs = glob.glob("/nix/store/*/bin/ffmpeg")
        print(f'FFmpeg en /nix/store: {nix_ffmpegs}')
    except Exception as e:
        print(f'Error buscando en /nix/store: {e}')
    
    # Intentar ejecutar ffmpeg para verificar
    try:
        result = subprocess.run([FFMPEG_PATH, "-version"], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg funcionando correctamente")
            # Mostrar primera línea de la versión
            first_line = result.stdout.split('\n')[0]
            print(f"Versión: {first_line}")
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
    except Exception as e:
        print(f"❌ Error al verificar FFmpeg: {e}")

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

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']

        source = discord.FFmpegPCMAudio(url2, executable=FFMPEG_PATH, **FFMPEG_OPTIONS)

        vc.stop()
        vc.play(source)

        await ctx.send(f"Reproduciendo: {info['title']}")
    except Exception as e:
        await ctx.send(f"Error al reproducir: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))