import discord
from discord.ext import commands
from config.config import TICKETS_CHANNEL

class TicketCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticket')
    async def ticket_command(self, ctx):
        embed = discord.Embed(color=65288)
        embed.set_image(url="https://i.imgur.com/cZuvDmH.gif")
        embed.title = "🎫 Como abrir un ticket"
        embed.description = f"""Dirígete a <#{TICKETS_CHANNEL}>. Ahí encontrarás un mensaje del bot. Haz click en el menú desplegable para abrir un ticket de la categoría que desees.
        
        Una vez ahí aparecerá un formulario que has de rellenar. ¡Cuantas más información aportes mejor se te atenderá!"""
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TicketCommand(bot))