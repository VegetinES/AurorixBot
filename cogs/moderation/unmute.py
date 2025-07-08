import discord
from discord.ext import commands
from discord import app_commands

from config.config import STAFF_ROLES, MUTE_ROLE_ID
from database.database import db
from cogs.logs.mod_logs import log_removal_sanction, send_dm_removal_sanction

class UnmuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        staff_roles = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        return bool(staff_roles.intersection(user_roles))

    @app_commands.command(name="unmute", description="Quitar el silencio a un usuario")
    @app_commands.describe(
        usuario="Usuario a des-silenciar",
        razon="Razón del des-silencio"
    )
    async def unmute(self, interaction: discord.Interaction, usuario: discord.User, razon: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        try:
            member = interaction.guild.get_member(usuario.id)
            if not member:
                await interaction.response.send_message("❌ El usuario no está en el servidor.", ephemeral=True)
                return

            mute_role = interaction.guild.get_role(MUTE_ROLE_ID)
            if not mute_role:
                await interaction.response.send_message("❌ El rol de silencio no existe.", ephemeral=True)
                return

            if mute_role not in member.roles:
                await interaction.response.send_message("❌ El usuario no está silenciado.", ephemeral=True)
                return
            
            await send_dm_removal_sanction(usuario, "Unmute", razon)
            
            await member.remove_roles(mute_role, reason=f"Unmute - {razon}")
            
            sanction_id = await db.create_sanction(
                user_id=usuario.id,
                moderator_id=interaction.user.id,
                sanction_type="unmute",
                reason=razon
            )
            
            await log_removal_sanction(interaction.guild, usuario, interaction.user, "Unmute", razon)
            
            await interaction.response.send_message(f"✅ {usuario.mention} ya no está silenciado. **Razón:** {razon}")
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos para des-silenciar a este usuario.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al des-silenciar al usuario: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnmuteCog(bot))