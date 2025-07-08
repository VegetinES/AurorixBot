import discord
from discord.ext import commands
from discord import app_commands

from config.config import STAFF_ROLES
from database.database import db
from cogs.logs.mod_logs import log_removal_sanction, send_dm_removal_sanction

class UnwarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        staff_roles = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        return bool(staff_roles.intersection(user_roles))

    @app_commands.command(name="unwarn", description="Eliminar una advertencia de un usuario")
    @app_commands.describe(
        sancion_id="ID de la sanción a eliminar"
    )
    async def unwarn(self, interaction: discord.Interaction, sancion_id: int):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        try:
            sanctions = await db.get_user_sanctions(None)
            sanction_found = None
            
            for sanction in sanctions:
                if sanction["sanction_id"] == sancion_id and sanction["sanction_type"] == "warn" and sanction["is_active"]:
                    sanction_found = sanction
                    break
            
            if not sanction_found:
                await interaction.response.send_message("❌ No se encontró una advertencia activa con ese ID.", ephemeral=True)
                return
            
            await db.remove_sanction(sancion_id)
            
            try:
                user = await self.bot.fetch_user(sanction_found["user_id"])
            except:
                user = None
            
            if user:
                await send_dm_removal_sanction(user, "Unwarn", f"Advertencia ID {sancion_id} removida")
                await log_removal_sanction(interaction.guild, user, interaction.user, "Unwarn", f"Advertencia ID {sancion_id} removida")
                await interaction.response.send_message(f"✅ Advertencia ID {sancion_id} de {user.mention} ha sido removida.")
            else:
                await interaction.response.send_message(f"✅ Advertencia ID {sancion_id} ha sido removida.")
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al eliminar la advertencia: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnwarnCog(bot))