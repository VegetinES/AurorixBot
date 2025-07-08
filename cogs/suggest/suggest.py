import discord
from discord.ext import commands

from cogs.suggest.suggest_buttons import SuggestionView
from config.config import SUGGEST_CHANNEL
from database.database import db

class SuggestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id != SUGGEST_CHANNEL:
            return

        suggestion_content = f"**Sugerencia**\n```\n{message.content}\n```"
        author = message.author
        guild = message.guild

        try:
            await message.delete()
        except discord.Forbidden:
            print(f"No se pudo eliminar el mensaje de {author.name}")
        except Exception as e:
            print(f"Error eliminando mensaje: {e}")

        embed = discord.Embed(
            title="Nueva sugerencia",
            description=suggestion_content,
            color=2326507
        )

        embed.set_image(url="https://i.imgur.com/WYZBgWJ.png")

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if author.avatar:
            footer_icon = author.avatar.url
        else:
            footer_icon = author.default_avatar.url

        embed.set_footer(text=f"Sugerencia de {author.name} | {author.id}", icon_url=footer_icon)

        try:
            view = SuggestionView()
            suggest_message = await message.channel.send(embed=embed, view=view)
            
            thread = await suggest_message.create_thread(
                name=f"Discusión: {suggestion_content[:50]}{'...' if len(suggestion_content) > 50 else ''}",
                auto_archive_duration=10080
            )
            
            thread_url = f"https://discord.com/channels/{thread.guild.id}/{thread.id}"
            await db.save_thread_url(suggest_message.id, thread_url)
            
            discussion_button = discord.ui.Button(
                label="Discusión", 
                style=discord.ButtonStyle.link, 
                emoji="💬", 
                url=thread_url
            )
            
            new_view = SuggestionView()
            new_view.add_item(discussion_button)
            await suggest_message.edit(view=new_view)
            
        except Exception as e:
            print(f"Error enviando sugerencia o creando hilo: {e}")

async def setup(bot):
    await bot.add_cog(SuggestCog(bot))