import os
import requests
import discord
from discord.ext import commands

# Configuración de credenciales desde Render
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_FOOTBALL_KEY
}

# Configuración de los permisos (Intents) de Discord
intents = discord.Intents.default()
intents.message_content = True  # Permite al bot leer los comandos en los canales

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 chiringitoBOT se ha conectado como {bot.user}")

# Comando de Clasificación (LaLiga ID: 140, Temporada: 2026)
@bot.command(name="clasificacion")
async def clasificacion(ctx):
    url = "https://api-sports.io"
    querystring = {"league": "140", "season": "2026"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=querystring)
        data = response.json()
        standings = data["response"]["league"]["standings"][0]  # Obtener la lista de posiciones
        
        mensaje = "📊 **Clasificación de LaLiga (2026/2027)** 📊\n\n"
        for team in standings[:10]:  # Muestra los 10 primeros equipos
            rank = team["rank"]
            name = team["team"]["name"]
            points = team["points"]
            mensaje += f"**{rank}.** {name} — {points} pts\n"
            
        await ctx.send(mensaje)
    except Exception as e:
        print(e)
        await ctx.send("❌ Error al conectar con API-Football para obtener la clasificación.")

# Comando de Fichajes
@bot.command(name="fichajes")
async def fichajes(ctx):
    mensaje = (
        "🔄 **Mercado de Fichajes (Muestra)** 🔄\n\n"
        "📌 *Jugador A* ➡️ Real Madrid (Confirmado)\n"
        "📌 *Jugador B* ➡️ FC Barcelona (Rumor)\n\n"
        "_(Próximamente: Conexión con transferencias en tiempo real)_"
    )
    await ctx.send(mensaje)

# Arrancar el bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
