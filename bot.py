import os
import requests
import discord
from discord.ext import commands

#Configuración de credenciales desde Render
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_FOOTBALL_KEY = osgetenv("API_FOOTBALL_KEY")

HEADERS = {
  "x-rapidapi-host": "v3.football.api-sports.io",
  "x-rapidapikey": API_FOOTBALL_KEY
}

#Configuración de los permisos (Intents) de Discord
intents = discord.Intents.default()
intents.message_content = True  # Permite al bot leer los mensajes en los canales
