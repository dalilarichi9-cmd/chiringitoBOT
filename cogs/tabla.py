import discord
from discord.ext import commands
import requests

class Tabla(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tabla')
    async def tabla(self, ctx):
        """Muestra la clasificación/tabla de posiciones de LaLiga EA Sports."""
        await ctx.send(f"📊 Buscando la clasificación de LaLiga EA Sports ({self.bot.CURRENT_SEASON})... Por favor, espera.")
        url = f"{self.bot.BASE_URL}/standings"
        params = {'league': self.bot.LALIGA_ID, 'season': self.bot.CURRENT_SEASON}
        
        try:
            response = requests.get(url, headers=self.bot.HEADERS, params=params).json()
            raw_response = response.get('response', [])
            if not raw_response:
                await ctx.send("❌ No se encontraron datos para la temporada actual.")
                return
                
            league_data = raw_response['league']
            # Estructura de API-Football: standings es una lista de listas, entramos al índice 0
            standings = league_data['standings']
            
            embed = discord.Embed(title="📊 Clasificación: LaLiga EA Sports", color=discord.Color.blue())
            descripcion = f"`#  Equipo       | PJ | PTS | DG`\n"
            for team in standings[:20]:  # Ampliado a 20 para mostrar todos los equipos de primera
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
            await ctx.send("❌ Ocurrió un error al procesar la clasificación.")

async def setup(bot):
    await bot.add_cog(Tabla(bot))

