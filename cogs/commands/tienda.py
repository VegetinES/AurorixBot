import discord
from discord.ext import commands

class TiendaCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tienda')
    async def tienda_command(self, ctx):
        embed = discord.Embed(color=8535199)
        embed.set_image(url="https://imgur.com/7Q6ruCf.png")
        embed.title = "🛒 Tus compras mantienen activo y actualizado el servidor, ¡Gracias!"
        embed.description = """Realiza tu compra sin problemas, recuerda lo siguiente️:

> 📍 Recuerda seleccionar bien la modalidad de tu compra
> 📍 Coloca bien tu nombre de usuario, de lo contrario no recibiras la compra
> 📍 Siempre pregunta si hay promociones para que las aproveches
> 📍 Si tienes problemas, abre ticket, el STAFF te ayudata"""
        
        view = discord.ui.View()
        button = discord.ui.Button(
            label="Ir a la tienda de Aurorixㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ",
            style=discord.ButtonStyle.link,
            emoji="🛒",
            url="https://tienda.aurorix.gg/"
        )
        view.add_item(button)
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TiendaCommand(bot))