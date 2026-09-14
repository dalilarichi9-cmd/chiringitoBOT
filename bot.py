import discord
from discord.ext import commands
import os
import asyncio
from keep_alive import keep_alive

class ChiringuitoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        
        # Constantes fijas exclusivas para LaLiga EA Sports
        self.BASE_URL = "https://api-sports.io"
        self.LALIGA_ID = 140
        self.CURRENT_SEASON = 2026  # Ajustado de forma nativa a la temporada actual en curso
        self.HEADERS = {'x-apisports-key': os.getenv('FOOTBALL_API_KEY')}

    async def setup_hook(self):
        # Carga automática de los comandos separados alojados en cogs/
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f'Cog cargado con éxito: {filename}')

bot = ChiringuitoBot()

@bot.event
async def on_ready():
    print(f'Conectado exitosamente como {bot.user.name} | Exclusivo LaLiga EA Sports')

@bot.command(name='ayuda')
async def ayuda(ctx):
    embed = discord.Embed(title="📋 Comandos de LaLiga EA Sports", color=discord.Color.gold())
    embed.add_field(name="`!tabla`", value="Muestra la clasificación de Primera División.", inline=False)
    embed.add_field(name="`!jornada`", value="Muestra los partidos de la jornada actual.", inline=False)
    embed.add_field(name="`!resultados`", value="Muestra los últimos 5 marcadores finalizados.", inline=False)
    embed.set_footer(text="Bot configurado en exclusiva para la liga española.")
    await ctx.send(embed=embed)

# Levantar servidor de Render y ejecutar bot
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))

