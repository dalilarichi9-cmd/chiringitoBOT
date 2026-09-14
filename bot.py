import discord
from discord.ext import commands
import requests
import os
import asyncio
from keep_alive import keep_alive

# Configuración de los Intents de Discord
intents = discord.Intents.default()
intents.message_content = True  # Indispensable

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Constantes fijas exclusivas para LaLiga EA Sports
BASE_URL = "https://api-sports.io"
LALIGA_ID = 140
CURRENT_SEASON = 2024  # Temporada liberada y estable para cuentas gratis
HEADERS = {'x-apisports-key': os.getenv('FOOTBALL_API_KEY')}

@bot.event
async def on_ready():
    print(f'🤖 ¡ChiringuitoBOT conectado con éxito como {bot.user.name}!')

@bot.command(name='ayuda')
async def ayuda(ctx):
    embed = discord.Embed(title="📋 Comandos de LaLiga EA Sports", color=discord.Color.gold())
    embed.add_field(name="`!tabla`", value="Muestra la clasificación de Primera División.", inline=False)
    embed.add_field(name="`!jornada`", value="Muestra los partidos de la jornada actual.", inline=False)
    embed.add_field(name="`!resultados`", value="Muestra los últimos 5 marcadores finalizados.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='tabla')
async def tabla(ctx):
    await ctx.send("📊 Buscando la clasificación de LaLiga... Por favor, espera.")
    url = f"{BASE_URL}/standings"
    params = {'league': LALIGA_ID, 'season': CURRENT_SEASON}
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        raw_response = response.get('response', [])
        if not raw_response:
            await ctx.send("❌ No se encontraron datos para la tabla en este momento.")
            return
        
        league_data = raw_response[0]['league']
        standings = league_data['standings'][0]
        
        embed = discord.Embed(title="📊 Clasificación: LaLiga EA Sports", color=discord.Color.blue())
        descripcion = f"`#  Equipo       | PJ | PTS | DG`\n"
        for team in standings[:20]:
            rank = str(team['rank']).ljust(2)
            name = team['team']['name'][:12].ljust(12)
            pj = str(team['all']['played']).ljust(2)
            pts = str(team['points']).ljust(3)
            dg = str(team['goalsDiff']).ljust(3)
            descripcion += f"`{rank} {name} | {pj} | {pts} | {dg}`\n"
            
        embed.description = descripcion
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error en tabla: {e}")
        await ctx.send("❌ Error al procesar la clasificación.")

@bot.command(name='jornada')
async def jornada(ctx):
    await ctx.send("🕒 Buscando la jornada actual... Por favor, espera.")
    try:
        round_url = f"{BASE_URL}/fixtures/rounds"
        round_params = {'league': LALIGA_ID, 'season': CURRENT_SEASON, 'current': 'true'}
        round_resp = requests.get(round_url, headers=HEADERS, params=round_params).json()
        current_round = round_resp.get('response', [])
        
        if not current_round:
            round_params.pop('current', None)
            round_resp = requests.get(round_url, headers=HEADERS, params=round_params).json()
            current_round = round_resp.get('response', [])
            
        round_name = current_round[0] if isinstance(current_round, list) else current_round
        
        fixtures_url = f"{BASE_URL}/fixtures"
        fixtures_params = {'league': LALIGA_ID, 'season': CURRENT_SEASON, 'round': round_name}
        fixtures_resp = requests.get(fixtures_url, headers=HEADERS, params=fixtures_params).json()
        fixtures = fixtures_resp.get('response', [])
        
        embed = discord.Embed(title=f"📅 Partidos - {round_name}", color=discord.Color.orange())
        for match in fixtures:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            status = match['fixture']['status']['short']
            
            if status in ['NS', 'TBD']:
                value = f"🕒 Fecha: {match['fixture']['date'][:10]} (Por jugar)"
            else:
                home_g = match['goals']['home'] if match['goals']['home'] is not None else 0
                away_g = match['goals']['away'] if match['goals']['away'] is not None else 0
                value = f"⚽ Marcador: **{home_g} - {away_g}** ({status})"
                
            embed.add_field(name=f"{home} vs {away}", value=value, inline=False)
            
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error en jornada: {e}")
        await ctx.send("❌ Error al obtener la jornada.")

@bot.command(name='resultados')
async def resultados(ctx):
    await ctx.send("🏁 Buscando los últimos marcadores... Por favor, espera.")
    url = f"{BASE_URL}/fixtures"
    params = {'league': LALIGA_ID, 'season': CURRENT_SEASON, 'status': 'FT', 'last': 5}
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        fixtures = response.get('response', [])
        if not fixtures:
            await ctx.send("❌ No se encontraron resultados registrados recientemente.")
            return
            
        embed = discord.Embed(title="🏁 Últimos Resultados: LaLiga EA Sports", color=discord.Color.red())
        for match in fixtures:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            home_g = match['goals']['home'] if match['goals']['home'] is not None else 0
            away_g = match['goals']['away'] if match['goals']['away'] is not None else 0
            embed.add_field(name=f"{home} vs {away}", value=f"Marcador final: **{home_g} - {away_g}**", inline=False)
            
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error en resultados: {e}")
        await ctx.send("❌ Error al consultar los marcadores.")

# Iniciar servidor web y bot de forma secuencial
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
