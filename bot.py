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

# Variables de Entorno de Render
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')

# Configuración oficial para cuentas directas de la web de API-Football
HEADERS = {
    'x-apisports-key': FOOTBALL_API_KEY
}
BASE_URL = "https://v3.football.api-sports.io"

# Diccionario de ligas comerciales mapeado a sus IDs oficiales
LIGAS = {
    "laliga": 140,
    "laligaeasports": 140,
    "easports": 140,
    "primera": 140,
    "primeradivision": 140,
    "espana": 140,
    
    "laligahypermotion": 141,
    "hypermotion": 141,
    "laliga2": 141,
    "segunda": 141,
    "segundadivision": 141,
    
    "premier": 39,
    "inglaterra": 39,
    "seriea": 135,
    "bundesliga": 78,
    "ligue1": 61,
    "champions": 2,
    "ucl": 2,
    "ligamx": 262,
    "mexico": 262
}

DEFAULT_LEAGUE_ID = 140
# 📅 Temporada ajustada al formato de indexación histórica y vigente del backend
CURRENT_SEASON = 2024

def obtener_league_id(nombre_liga: str) -> int:
    """Busca la liga limpiando el texto si el usuario escribe algo."""
    if not nombre_liga or nombre_liga.strip() == "":
        return DEFAULT_LEAGUE_ID
    
    nombre_limpio = (nombre_liga.lower()
                     .strip()
                     .replace(" ", "")
                     .replace("-", "")
                     .replace("á", "a")
                     .replace("é", "e")
                     .replace("í", "i")
                     .replace("ó", "o")
                     .replace("ú", "u"))
    
    return LIGAS.get(nombre_limpio, None)


@bot.event
async def on_ready():
    print(f'Conectado exitosamente como {bot.user.name}')

@bot.event
async def on_command_completion(ctx):
    print(f'✅ Comando !{ctx.command.name} ejecutado con éxito por {ctx.author}')


@bot.command(name='tabla')
async def tabla(ctx, *, liga: str = ""):
    """Muestra la clasificación/tabla de posiciones."""
    league_id = obtener_league_id(liga)
    
    if league_id is None:
        await ctx.send(f"❌ No reconozco la liga '{liga}'. Intenta con: `laliga`, `hypermotion`...")
        return

    await ctx.send("📊 Buscando la clasificación... Por favor, espera.")
    url = f"{BASE_URL}/standings"
    params = {'league': league_id, 'season': CURRENT_SEASON}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        raw_response = response.get('response', [])
        
        if not raw_response:
            await ctx.send(f"❌ No se encontró la clasificación para la temporada {CURRENT_SEASON}.")
            return
            
        # 🛠️ CORRECCIÓN CLAVE: Entrar al primer objeto de la lista response
        league_data = raw_response[0]['league']
        league_name = league_data['name']
        
        # Standings es una lista de listas en la respuesta JSON oficial de la API
        standings = league_data['standings'][0]
        
        embed = discord.Embed(title=f"📊 Clasificación: {league_name} ({CURRENT_SEASON})", color=discord.Color.blue())
        
        descripcion = f"`Pos. Equipo          | PJ | Pts | DG`\n"
        for team in standings[:15]:
            rank = str(team['rank']).ljust(3)
            name = team['team']['name'][:13].ljust(15)
            pj = str(team['all']['played']).ljust(2)
            pts = str(team['points']).ljust(3)
            dg = str(team['goalsDiff']).ljust(3)
            descripcion += f"`{rank} {name} | {pj} | {pts} | {dg}`\n"
            
        embed.description = descripcion
        embed.set_footer(text="Usa !tabla [nombre_liga] para cambiar de competición.")
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error detallado en tabla: {e}")
        await ctx.send("❌ Ocurrió un error al procesar los datos de la clasificación.")


@bot.command(name='jornada')
async def jornada(ctx, *, liga: str = ""):
    """Busca los partidos de la jornada actual."""
    league_id = obtener_league_id(liga)
    
    if league_id is None:
        await ctx.send(f"❌ No reconozco la liga '{liga}'.")
        return

    await ctx.send("🕒 Buscando la jornada actual... Por favor, espera.")
    
    try:
        round_url = f"{BASE_URL}/fixtures/rounds"
        round_params = {'league': league_id, 'season': CURRENT_SEASON, 'current': 'true'}
        round_resp = requests.get(round_url, headers=HEADERS, params=round_params).json()
        current_round = round_resp.get('response', [])
        
        if not current_round:
            await ctx.send("❌ No se pudo determinar la jornada activa.")
            return
            
        # 🛠️ CORRECCIÓN CLAVE: El endpoint devuelve una lista. Extraemos el primer texto
        round_name = current_round[0]
        
        fixtures_url = f"{BASE_URL}/fixtures"
        fixtures_params = {'league': league_id, 'season': CURRENT_SEASON, 'round': round_name}
        fixtures_resp = requests.get(fixtures_url, headers=HEADERS, params=fixtures_params).json()
        fixtures = fixtures_resp.get('response', [])
        
        embed = discord.Embed(title=f"📅 Partidos - {round_name}", color=discord.Color.orange())
        
        for match in fixtures[:11]:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            status = match['fixture']['status']['short']
            
            if status in ['NS', 'TBD']:
                raw_date = match['fixture']['date'][:10]
                value = f"🕒 Fecha: {raw_date} (Por jugar)"
            else:
                home_g = match['goals']['home']
                away_g = match['goals']['away']
                value = f"⚽ Resultado: **{home_g} - {away_g}** ({status})"
                
            embed.add_field(name=f"{home} vs {away}", value=value, inline=False)
            
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error en jornada: {e}")
        await ctx.send("❌ Ocurrió un error al obtener el calendario de la jornada.")


@bot.command(name='resultados')
async def resultados(ctx, *, liga: str = ""):
    """Muestra los últimos 5 resultados."""
    league_id = obtener_league_id(liga)
    
    if league_id is None:
        await ctx.send(f"❌ No reconozco la liga '{liga}'.")
        return

    await ctx.send("🏁 Buscando los últimos marcadores... Por favor, espera.")
    url = f"{BASE_URL}/fixtures"
    params = {'league': league_id, 'season': CURRENT_SEASON, 'last': 5}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        fixtures = response.get('response', [])
        
        if not fixtures:
            await ctx.send("❌ No se encontraron resultados registrados recientemente.")
            return
            
        embed = discord.Embed(title="🏁 Últimos Resultados", color=discord.Color.red())
        
        for match in fixtures:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            home_g = match['goals']['home']
            away_g = match['goals']['away']
            embed.add_field(
                name=f"{home} vs {away}", 
                value=f"Marcador final: **{home_g} - {away_g}**", 
                inline=False
            )
            
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error en resultados: {e}")
        await ctx.send("❌ Ocurrió un error al consultar los marcadores recientes.")


@bot.command(name='estadisticas')
async def estadisticas(ctx, fixture_id: int):
    """Muestra las estadísticas de juego usando el ID numérico del partido."""
    await ctx.send(f"📊 Buscando estadísticas del partido {fixture_id}... Por favor, espera.")
    url = f"{BASE_URL}/fixtures/statistics"
    params = {'fixture': fixture_id}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params).json()
        stats_data = response.get('response', [])
        
        if not stats_data or len(stats_data) < 2:
            await ctx.send("❌ No hay estadísticas disponibles. Asegúrate de ingresar un ID válido.")
            return
            
        # Extraemos las dos partes correspondientes a los dos rivales del array response
        team1_data = stats_data[0]
        team2_data = stats_data[1]
        
        team1 = team1_data['team']['name']
        team2 = team2_data['team']['name']
        
        embed = discord.Embed(title=f"📊 Estadísticas del Encuentro", description=f"**{team1} vs {team2}**", color=discord.Color.purple())
        
        t1_stats = {s['type']: s['value'] for s in team1_data['statistics']}
        t2_stats = {s['type']: s['value'] for s in team2_data['statistics']}
        
        metricas = [
            ('Ball Possession', 'Posesión'),
            ('Total Shots', 'Remates Totales'),
            ('Shots on Goal', 'Tiros al Arco'),
            ('Corner Kicks', 'Córners'),
            ('Fouls', 'Faltas')
        ]
        
        for api_key, nombre_es in metricas:
            v1 = t1_stats.get(api_key, 0) or 0
            v2 = t2_stats.get(api_key, 0) or 0
            embed.add_field(name=nombre_es, value=f"{team1}: **{v1}** | {team2}: **{v2}**", inline=False)
            
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error en estadísticas: {e}")
        await ctx.send("❌ Error al procesar las estadísticas del encuentro.")

# Iniciar servidor
keep_alive()
bot.run(DISCORD_TOKEN)

