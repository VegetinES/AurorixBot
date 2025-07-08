import discord
from discord.ext import commands

class DiscordCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='discord')
    async def discord_command(self, ctx):
        embed = discord.Embed(color=54015)
        embed.title = "¿Te gusta jugar en un servidor con buen ambiente, apoyo entre jugadores y eventos divertidos?"
        embed.description = """Entonces ¡no te puedes quedar fuera de nuestro Discord! 🗨️

> 🔹 Resuelve tus dudas rápidamente
> 🔹 Recibe noticias y anuncios antes que nadie
> 🔹 Participa en sorteos, eventos y minijuegos
> 🔹 Habla con otros jugadores, haz amigos o forma clanes
> 🔹 Soporte directo del staff y sistema de tickets"""
        embed.url = "https://discord.aurorix.online/"
        embed.set_image(url="https://dunb17ur4ymx4.cloudfront.net/webstore/logos/a1e8e7584c0b9c8ebb3c7fe926398243c505d82d.png")
        
        view = discord.ui.View()
        button = discord.ui.Button(
            label="Servidor de Discordㅤㅤㅤㅤㅤㅤㅤ ㅤㅤㅤㅤㅤ ㅤㅤㅤㅤ",
            style=discord.ButtonStyle.link,
            emoji="⭐",
            url="https://discord.aurorix.online/"
        )
        view.add_item(button)
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(DiscordCommand(bot))