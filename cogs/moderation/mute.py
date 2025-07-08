import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import re

from config.config import STAFF_ROLES, MUTE_ROLE_ID
from database.database import db
from cogs.logs.mod_logs import log_sanction, send_dm_sanction

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        staff_roles = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        return bool(staff_roles.intersection(user_roles))

    def parse_duration(self, duration_str):
        match = re.match(r'^(\d+)([smh])$', duration_str.lower())
        if not match:
            return None
        
        amount, unit = match.groups()
        amount = int(amount)
        
        if unit == 's':
            return timedelta(seconds=amount)
        elif unit == 'm':
            return timedelta(minutes=amount)
        elif unit == 'h':
            return timedelta(hours=amount)
        
        return None

    @app_commands.command(name="mute", description="Silenciar a un usuario permanentemente")
    @app_commands.describe(
        usuario="Usuario a silenciar",
        razon="Razón del silencio"
    )
    async def mute(self, interaction: discord.Interaction, usuario: discord.User, razon: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        try:
            member = interaction.guild.get_member(usuario.id)
            if not member:
                await interaction.response.send_message("❌ El usuario no está en el servidor.", ephemeral=True)
                return

            if self.has_staff_permissions(member):
                await interaction.response.send_message("❌ No puedes silenciar a un miembro del staff.", ephemeral=True)
                return

            mute_role = interaction.guild.get_role(MUTE_ROLE_ID)
            if not mute_role:
                await interaction.response.send_message("❌ El rol de silencio no existe.", ephemeral=True)
                return

            if mute_role in member.roles:
                await interaction.response.send_message("❌ El usuario ya está silenciado.", ephemeral=True)
                return

            await send_dm_sanction(usuario, "Mute", razon)
            
            await member.add_roles(mute_role, reason=f"Mute - {razon}")
            
            sanction_id = await db.create_sanction(
                user_id=usuario.id,
                moderator_id=interaction.user.id,
                sanction_type="mute",
                reason=razon
            )
            
            await log_sanction(interaction.guild, usuario, interaction.user, "Mute", razon)
            
            await interaction.response.send_message(f"✅ {usuario.mention} ha sido silenciado permanentemente. **Razón:** {razon}")
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos para silenciar a este usuario.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al silenciar al usuario: {str(e)}", ephemeral=True)

    @app_commands.command(name="tempmute", description="Silenciar a un usuario temporalmente")
    @app_commands.describe(
        usuario="Usuario a silenciar",
        tiempo="Duración del silencio (ej: 30s, 5m, 2h)",
        razon="Razón del silencio"
    )
    async def tempmute(self, interaction: discord.Interaction, usuario: discord.User, tiempo: str, razon: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        duration = self.parse_duration(tiempo)
        if not duration:
            await interaction.response.send_message("❌ Formato de tiempo inválido. Usa: 30s, 5m, 2h", ephemeral=True)
            return

        try:
            member = interaction.guild.get_member(usuario.id)
            if not member:
                await interaction.response.send_message("❌ El usuario no está en el servidor.", ephemeral=True)
                return

            if self.has_staff_permissions(member):
                await interaction.response.send_message("❌ No puedes silenciar a un miembro del staff.", ephemeral=True)
                return

            mute_role = interaction.guild.get_role(MUTE_ROLE_ID)
            if not mute_role:
                await interaction.response.send_message("❌ El rol de silencio no existe.", ephemeral=True)
                return

            if mute_role in member.roles:
                await interaction.response.send_message("❌ El usuario ya está silenciado.", ephemeral=True)
                return

            expires_at = datetime.now() + duration
            
            await send_dm_sanction(usuario, "Mute Temporal", f"{razon} - Duración: {tiempo}")
            
            await member.add_roles(mute_role, reason=f"Mute temporal ({tiempo}) - {razon}")
            
            sanction_id = await db.create_sanction(
                user_id=usuario.id,
                moderator_id=interaction.user.id,
                sanction_type="tempmute",
                reason=f"{razon} - Duración: {tiempo}",
                duration=expires_at
            )
            
            await log_sanction(interaction.guild, usuario, interaction.user, "Mute Temporal", f"{razon} - Duración: {tiempo}")
            
            await interaction.response.send_message(f"✅ {usuario.mention} ha sido silenciado por {tiempo}. **Razón:** {razon}")
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos para silenciar a este usuario.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al silenciar al usuario: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MuteCog(bot))