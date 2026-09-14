# bot.py
import discord
from discord.ext import commands
import requests
import os
from datetime import datetime
from keep_alive import keep_alive

# Configuración de los Intents de Discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Variables de Entorno (Se configuran en Render)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')

@bot.event
async def on_ready():
    print(f'Conectado exitosamente como {bot.user.name}')

@bot.command(name='partidos')
async def partidos(ctx, league_id: int = 140): # Por defecto 140 es LaLiga de España
    """Muestra los partidos del día de hoy para una liga específica."""
    await ctx.send("⚽ Buscando partidos de hoy... Por favor, espera.")
    
    url = "https://api-sports.io"
    today = datetime.today().strftime('%Y-%m-%d')
    
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': FOOTBALL_API_KEY
    }
    
    params = {
        'date': today,
        'league': league_id,
        'season': datetime.today().year if datetime.today().month > 6 else datetime.today().year - 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params).json()
        fixtures = response.get('response', [])
        
        if not fixtures:
            await ctx.send(f"📅 No hay partidos programados para hoy en esta liga (ID: {league_id}).")
            return
            
        embed = discord.Embed(title=f"🏆 Partidos de Hoy", color=discord.Color.green())
        
        for match in fixtures:
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            status = match['fixture']['status']['short']
            
            # Si el partido ya empezó o terminó, muestra goles
            if status in ['1H', '2H', 'HT', 'FT']:
                home_goals = match['goals']['home']
                away_goals = match['goals']['away']
                score = f"[{home_goals} - {away_goals}]"
            else:
                # Mostrar hora del partido en UTC
                match_time = match['fixture']['date'].split('T')[1][:5]
                score = f"🕒 {match_time} UTC"
                
            embed.add_field(
                name=f"{home_team} vs {away_team}",
                value=f"Estado: {status} | Resultado: {score}",
                inline=False
            )
            
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(e)
        await ctx.send("❌ Error al conectar con la API de fútbol.")

# Iniciar servidor web para Render antes de arrancar el bot
keep_alive()

# Ejecutar el bot
bot.run(DISCORD_TOKEN)

