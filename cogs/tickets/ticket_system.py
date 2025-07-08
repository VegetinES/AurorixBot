import discord
from discord.ext import commands
from discord import app_commands

from config.config import TICKETS_CHANNEL, STAFF_ROLES
from .ticket_views import TicketSelectView

class TicketSystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_admin_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        admin_role_id = STAFF_ROLES["Admin"]
        return admin_role_id in user_roles

    @commands.command(name="ticketcreate")
    async def ticket_create(self, ctx, *, password=None):
        try:
            await ctx.message.delete()
        except:
            pass

        if not self.has_admin_permissions(ctx.author):
            return
        
        if password != "password123":  # Cambia esto por la contraseña que quieras
            return

        embed = discord.Embed(
            title="📬 Centro de SOPORTE",
            description="Selecciona la categoría que más se adecue con tu necesidad y creamos un ticket por ti.\n\nDe esta forma podrás ponerte en contacto con uno de nuestros miembros del equipo y así ayudarte a solucionar tu problema.\n\nRecomendamos habilitar los mensajes directos dentro del servidor para estar notificado de cualquier cambio.",
            color=2354125
        )
        
        if ctx.guild.icon:
            embed.set_footer(text=" Aurorix | Gestión de Tickets", icon_url=ctx.guild.icon.url)
        else:
            embed.set_footer(text=" Aurorix | Gestión de Tickets")

        channel = self.bot.get_channel(TICKETS_CHANNEL)
        if channel:
            view = TicketSelectView()
            await channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TicketSystemCog(bot))