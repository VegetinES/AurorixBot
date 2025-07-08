import discord
from discord.ext import commands
from discord import app_commands

from config.config import STAFF_ROLES
from database.database import db
from cogs.logs.mod_logs import log_sanction, send_dm_sanction

class KickCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        staff_roles = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        return bool(staff_roles.intersection(user_roles))

    @app_commands.command(name="kick", description="Expulsar a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a expulsar",
        razon="Razón de la expulsión"
    )
    async def kick(self, interaction: discord.Interaction, usuario: discord.User, razon: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        try:
            member = interaction.guild.get_member(usuario.id)
            if not member:
                await interaction.response.send_message("❌ El usuario no está en el servidor.", ephemeral=True)
                return

            if self.has_staff_permissions(member):
                await interaction.response.send_message("❌ No puedes expulsar a un miembro del staff.", ephemeral=True)
                return

            await send_dm_sanction(usuario, "Kick", razon)
            
            await interaction.guild.kick(member, reason=razon)
            
            sanction_id = await db.create_sanction(
                user_id=usuario.id,
                moderator_id=interaction.user.id,
                sanction_type="kick",
                reason=razon
            )
            
            await log_sanction(interaction.guild, usuario, interaction.user, "Kick", razon)
            
            await interaction.response.send_message(f"✅ {usuario.mention} ha sido expulsado del servidor. **Razón:** {razon}")
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos para expulsar a este usuario.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al expulsar al usuario: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(KickCog(bot))