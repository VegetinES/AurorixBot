import discord
from discord.ext import commands
from discord import app_commands

from cogs.suggest.suggest_buttons import clear_suggestion_data
from config.config import STAFF_ROLES, SUGGEST_CHANNEL

class ReasonModal(discord.ui.Modal):
    def __init__(self, action_type, message, bot):
        super().__init__(title=f"Razón para {action_type}")
        self.action_type = action_type
        self.message = message
        self.bot = bot
        
        self.reason_input = discord.ui.TextInput(
            label="Razón (opcional)",
            placeholder="Escribe la razón de tu decisión...",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000
        )
        self.add_item(self.reason_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value.strip() if self.reason_input.value else None
        
        embed = self.message.embeds[0]
        
        existing_reason = None
        if embed.fields:
            for field in embed.fields:
                if field.name == "Razón":
                    existing_reason = field.value.strip("```\n")
                    break
        
        final_reason = reason if reason else existing_reason
        
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
            title=action_titles[self.action_type],
            description=embed.description,
            color=action_colors[self.action_type]
        )
        
        new_embed.set_image(url=action_images[self.action_type])
        
        if final_reason:
            new_embed.add_field(name="Razón", value=f"```\n{final_reason}\n```", inline=False)
        
        if embed.thumbnail:
            new_embed.set_thumbnail(url=embed.thumbnail.url)
        
        if embed.footer:
            new_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)

        try:
            await self.message.edit(embed=new_embed, view=None)
            await self.close_suggestion_thread()
            await clear_suggestion_data(self.message.id)
            
            action_names = {
                "aceptar": "aceptada",
                "rechazar": "rechazada",
                "implementado": "marcada como implementada"
            }
            
            await interaction.response.send_message(
                f"✅ Sugerencia {action_names[self.action_type]} correctamente.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message("❌ Error al actualizar la sugerencia.", ephemeral=True)

    async def close_suggestion_thread(self):
        try:
            if hasattr(self.message, 'thread') and self.message.thread:
                thread = self.message.thread
                await thread.edit(archived=True, locked=True)
            else:
                channel = self.message.channel
                if hasattr(channel, 'parent') and channel.parent:
                    threads = channel.threads
                    for thread in threads:
                        if thread.name.startswith("Discusión:") and thread.id in [t.id for t in await channel.active_threads()]:
                            await thread.edit(archived=True, locked=True)
                            break
        except Exception as e:
            print(f"Error cerrando hilo: {e}")

def has_admin_permissions(member):
    user_roles = {role.id for role in member.roles}
    admin_role_id = STAFF_ROLES["Admin"]
    return admin_role_id in user_roles

def is_valid_suggestion(message, bot):
    if message.channel.id != SUGGEST_CHANNEL:
        return False
    
    if not message.author.bot or message.author.id != bot.user.id:
        return False
    
    if not message.embeds:
        return False
    
    embed_title = message.embeds[0].title
    valid_titles = ["Nueva sugerencia", "✅ Sugerencia Aceptada"]
    
    if embed_title not in valid_titles:
        return False
    
    return True

def is_accepted_suggestion(message):
    if not message.embeds:
        return False
    return message.embeds[0].title == "✅ Sugerencia Aceptada"

@app_commands.context_menu(name="Aceptar Sugerencia")
async def accept_suggestion(interaction: discord.Interaction, message: discord.Message):
    if not has_admin_permissions(interaction.user):
        await interaction.response.send_message("❌ No tienes permisos para usar esta función.", ephemeral=True)
        return
    
    if not is_valid_suggestion(message, interaction.client):
        await interaction.response.send_message("❌ Esta acción solo funciona con sugerencias por gestionar.", ephemeral=True)
        return
    
    if is_accepted_suggestion(message):
        await interaction.response.send_message("❌ Esta sugerencia ya está aceptada. Solo puedes marcarla como implementada.", ephemeral=True)
        return
    
    modal = ReasonModal("aceptar", message, interaction.client)
    await interaction.response.send_modal(modal)

@app_commands.context_menu(name="Rechazar Sugerencia")
async def reject_suggestion(interaction: discord.Interaction, message: discord.Message):
    if not has_admin_permissions(interaction.user):
        await interaction.response.send_message("❌ No tienes permisos para usar esta función.", ephemeral=True)
        return
    
    if not is_valid_suggestion(message, interaction.client):
        await interaction.response.send_message("❌ Esta acción solo funciona con sugerencias por gestionar.", ephemeral=True)
        return
    
    if is_accepted_suggestion(message):
        await interaction.response.send_message("❌ Esta sugerencia ya está aceptada. Solo puedes marcarla como implementada.", ephemeral=True)
        return
    
    modal = ReasonModal("rechazar", message, interaction.client)
    await interaction.response.send_modal(modal)

@app_commands.context_menu(name="Ya Implementado")
async def implemented_suggestion(interaction: discord.Interaction, message: discord.Message):
    if not has_admin_permissions(interaction.user):
        await interaction.response.send_message("❌ No tienes permisos para usar esta función.", ephemeral=True)
        return
    
    if not is_valid_suggestion(message, interaction.client):
        await interaction.response.send_message("❌ Esta acción solo funciona con sugerencias por gestionar.", ephemeral=True)
        return
    
    modal = ReasonModal("implementado", message, interaction.client)
    await interaction.response.send_modal(modal)

class SuggestContextMenuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    bot.tree.add_command(accept_suggestion)
    bot.tree.add_command(reject_suggestion)
    bot.tree.add_command(implemented_suggestion)
    await bot.add_cog(SuggestContextMenuCog(bot))