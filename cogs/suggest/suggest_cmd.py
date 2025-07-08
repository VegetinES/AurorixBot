import discord
from discord.ext import commands
from discord import app_commands

from cogs.suggest.suggest_buttons import clear_suggestion_data
from config.config import STAFF_ROLES

class SuggestCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_admin_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        admin_role_id = STAFF_ROLES["Admin"]
        return admin_role_id in user_roles

    def is_valid_suggestion(self, message):
        if not message.embeds:
            return False
        
        embed_title = message.embeds[0].title
        valid_titles = ["Nueva sugerencia", "✅ Sugerencia Aceptada"]
        
        return embed_title in valid_titles

    def is_accepted_suggestion(self, message):
        if not message.embeds:
            return False
        return message.embeds[0].title == "✅ Sugerencia Aceptada"

    async def close_suggestion_thread(self, message):
        try:
            if hasattr(message, 'thread') and message.thread:
                thread = message.thread
                await thread.edit(archived=True, locked=True)
            else:
                channel = message.channel
                if hasattr(channel, 'parent') and channel.parent:
                    threads = channel.threads
                    for thread in threads:
                        if thread.name.startswith("Discusión:") and thread.id in [t.id for t in await channel.active_threads()]:
                            await thread.edit(archived=True, locked=True)
                            break
        except Exception as e:
            print(f"Error cerrando hilo: {e}")

    @app_commands.command(name="sugerencia", description="Gestionar sugerencias")
    @app_commands.describe(
        sugerencia="ID del mensaje de la sugerencia",
        accion="Acción a realizar con la sugerencia",
        razon="Razón de la decisión (opcional)"
    )
    @app_commands.choices(accion=[
        app_commands.Choice(name="Aceptar", value="aceptar"),
        app_commands.Choice(name="Rechazar", value="rechazar"),
        app_commands.Choice(name="Implementado", value="implementado")
    ])
    async def sugerencia_cmd(self, interaction: discord.Interaction, sugerencia: str, accion: app_commands.Choice[str], razon: str = None):
        if not self.has_admin_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para usar esta función.", ephemeral=True)
            return

        try:
            message_id = int(sugerencia)
        except ValueError:
            await interaction.response.send_message("❌ El ID del mensaje es incorrecto.", ephemeral=True)
            return

        try:
            message = await interaction.channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message("❌ El ID del mensaje es incorrecto.", ephemeral=True)
            return
        except Exception:
            await interaction.response.send_message("❌ El ID del mensaje es incorrecto.", ephemeral=True)
            return

        if not self.is_valid_suggestion(message):
            await interaction.response.send_message("❌ El ID del mensaje es incorrecto.", ephemeral=True)
            return

        is_accepted = self.is_accepted_suggestion(message)
        
        if is_accepted and accion.value != "implementado":
            await interaction.response.send_message("❌ Esta sugerencia ya está aceptada. Solo puedes marcarla como implementada.", ephemeral=True)
            return

        embed = message.embeds[0]
        
        existing_reason = None
        if embed.fields:
            for field in embed.fields:
                if field.name == "Razón":
                    existing_reason = field.value.strip("```\n")
                    break
        
        final_reason = razon if razon else existing_reason
        
        action_colors = {
            "aceptar": 0x00FF00,
            "rechazar": 0xFF0000,
            "implementado": 0x0099FF
        }
        
        action_titles = {
            "aceptar": "✅ Sugerencia Aceptada",
            "rechazar": "❌ Sugerencia Rechazada", 
            "implementado": "ℹ️ Ya Implementado"
        }

        action_images = {
            "aceptar": "https://i.imgur.com/9webzF5.png",
            "rechazar": "https://i.imgur.com/Bm36cjv.png",
            "implementado": "https://i.imgur.com/WYZBgWJ.png"
        }

        new_embed = discord.Embed(
            title=action_titles[accion.value],
            description=embed.description,
            color=action_colors[accion.value]
        )
        
        new_embed.set_image(url=action_images[accion.value])
        
        if final_reason:
            new_embed.add_field(name="Razón", value=f"```\n{final_reason}\n```", inline=False)
        
        if embed.thumbnail:
            new_embed.set_thumbnail(url=embed.thumbnail.url)
        
        if embed.footer:
            new_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)

        try:
            await message.edit(embed=new_embed, view=None)
            await self.close_suggestion_thread(message)
            await clear_suggestion_data(message_id)
            await interaction.response.send_message(f"✅ Sugerencia {accion.name.lower()} correctamente.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("❌ Error al actualizar la sugerencia.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SuggestCommandCog(bot))