import discord
from discord.ext import commands
from discord import app_commands

from config.config import STAFF_ROLES
from database.database import db
from cogs.logs.mod_logs import log_removal_sanction

class UnbanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        staff_roles = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        return bool(staff_roles.intersection(user_roles))

    @app_commands.command(name="unban", description="Desbanear a un usuario")
    @app_commands.describe(
        usuario="Usuario a desbanear (ID o nombre#discriminator)",
        razon="Razón del desbaneo"
    )
    async def unban(self, interaction: discord.Interaction, usuario: str, razon: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        try:
            user_to_unban = None
            
            if usuario.isdigit():
                user_id = int(usuario)
                try:
                    user_to_unban = await self.bot.fetch_user(user_id)
                except discord.NotFound:
                    await interaction.response.send_message("❌ Usuario no encontrado.", ephemeral=True)
                    return
            else:
                banned_users = [entry async for entry in interaction.guild.bans()]
                for ban_entry in banned_users:
                    if str(ban_entry.user) == usuario or ban_entry.user.name.lower() == usuario.lower():
                        user_to_unban = ban_entry.user
                        break
            
            if not user_to_unban:
                await interaction.response.send_message("❌ Usuario no encontrado en la lista de baneados.", ephemeral=True)
                return
            
            await interaction.guild.unban(user_to_unban, reason=razon)
            
            sanction_id = await db.create_sanction(
                user_id=user_to_unban.id,
                moderator_id=interaction.user.id,
                sanction_type="unban",
                reason=razon
            )
            
            await log_removal_sanction(interaction.guild, user_to_unban, interaction.user, "Unban", razon)
            
            await interaction.response.send_message(f"✅ {user_to_unban.mention} ha sido desbaneado. **Razón:** {razon}")
            
        except discord.NotFound:
            await interaction.response.send_message("❌ El usuario no está baneado.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos para desbanear usuarios.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al desbanear al usuario: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnbanCog(bot))