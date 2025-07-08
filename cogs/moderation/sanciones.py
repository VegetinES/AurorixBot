import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import math

from config.config import STAFF_ROLES
from database.database import db

class SancionesView(discord.ui.View):
    def __init__(self, user, sanctions, total_sanctions, current_page=0, per_page=5):
        super().__init__(timeout=30)
        self.user = user
        self.sanctions = sanctions
        self.total_sanctions = total_sanctions
        self.current_page = current_page
        self.per_page = per_page
        self.total_pages = math.ceil(total_sanctions / per_page)
        
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1

    def create_embed(self):
        embed = discord.Embed(
            title=f"📋 Sanciones de {self.user.display_name}",
            color=0xff9900
        )
        
        embed.set_thumbnail(url=self.user.display_avatar.url)
        
        if not self.sanctions:
            embed.description = "Este usuario no tiene sanciones registradas."
            return embed
        
        start_idx = self.current_page * self.per_page
        end_idx = start_idx + self.per_page
        current_sanctions = self.sanctions[start_idx:end_idx]
        
        for sanction in current_sanctions:
            sanction_type = sanction["sanction_type"].title()
            if sanction_type == "Tempban":
                sanction_type = "Baneo Temporal"
            
            status = "🟢 Activa" if sanction["is_active"] else "🔴 Inactiva"
            
            timestamp = int(sanction["created_at"].timestamp())
            
            moderator_id = sanction["moderator_id"]
            
            field_value = f"**Razón:** {sanction['reason']}\n"
            field_value += f"**Moderador:** <@{moderator_id}> (`{moderator_id}`)\n"
            field_value += f"**Fecha:** <t:{timestamp}:F> (<t:{timestamp}:R>)\n"
            field_value += f"**Estado:** {status}"
            
            embed.add_field(
                name=f"{sanction_type} - ID: {sanction['sanction_id']}",
                value=field_value,
                inline=False
            )
        
        embed.set_footer(
            text=f"Página {self.current_page + 1}/{self.total_pages} • Total: {self.total_sanctions} sanciones"
        )
        
        return embed

    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            start_idx = self.current_page * self.per_page
            end_idx = start_idx + self.per_page
            
            self.sanctions = await db.get_user_sanctions(
                self.user.id, 
                limit=self.per_page,
                skip=start_idx
            )
            
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Siguiente ▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            start_idx = self.current_page * self.per_page
            end_idx = start_idx + self.per_page
            
            self.sanctions = await db.get_user_sanctions(
                self.user.id,
                limit=self.per_page,
                skip=start_idx
            )
            
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

class SancionesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        staff_roles = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        return bool(staff_roles.intersection(user_roles))

    @app_commands.command(name="sanciones", description="Ver las sanciones de un usuario")
    @app_commands.describe(
        usuario="Usuario del que ver las sanciones"
    )
    async def sanciones(self, interaction: discord.Interaction, usuario: discord.User):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return

        try:
            total_sanctions = await db.count_user_sanctions(usuario.id)
            
            if total_sanctions == 0:
                embed = discord.Embed(
                    title=f"📋 Sanciones de {usuario.display_name}",
                    description="Este usuario no tiene sanciones registradas.",
                    color=0x00ff00
                )
                embed.set_thumbnail(url=usuario.display_avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            sanctions = await db.get_user_sanctions(usuario.id, limit=5, skip=0)
            
            view = SancionesView(usuario, sanctions, total_sanctions)
            embed = view.create_embed()
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al obtener las sanciones: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SancionesCog(bot))