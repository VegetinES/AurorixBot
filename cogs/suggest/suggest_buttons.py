import discord
from discord.ext import commands
from database.database import db

class SuggestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def calculate_percentages(self, message_id):
        votes = await db.get_votes(message_id)
        yes_votes = len(votes["yes"])
        no_votes = len(votes["no"])
        total_votes = yes_votes + no_votes
        
        if total_votes == 0:
            return 0, 0
        
        yes_percentage = round((yes_votes / total_votes) * 100)
        no_percentage = round((no_votes / total_votes) * 100)
        
        return yes_percentage, no_percentage

    @discord.ui.button(label="Sí (0%)", style=discord.ButtonStyle.success, emoji="✅", custom_id="suggest_yes")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_id = interaction.message.id
        user_id = interaction.user.id
        current_vote = await db.has_voted(message_id, user_id)
        
        if current_vote == "yes":
            await db.remove_vote(message_id, user_id)
            await interaction.response.send_message("❌ Has quitado tu voto de Sí", ephemeral=True)
        else:
            await db.add_vote(message_id, user_id, "yes")
            await interaction.response.send_message("✅ Has votado Sí", ephemeral=True)
        
        yes_percentage, no_percentage = await self.calculate_percentages(message_id)
        
        new_view = SuggestionView()
        new_view.yes_button.label = f"Sí ({yes_percentage}%)"
        new_view.no_button.label = f"No ({no_percentage}%)"
        
        thread_url = await db.get_thread_url(message_id)
        if thread_url:
            discussion_button = discord.ui.Button(
                label="Discusión", 
                style=discord.ButtonStyle.link, 
                emoji="💬", 
                url=thread_url
            )
            new_view.add_item(discussion_button)
        
        try:
            await interaction.message.edit(view=new_view)
        except Exception as e:
            print(f"Error actualizando mensaje: {e}")

    @discord.ui.button(label="No (0%)", style=discord.ButtonStyle.danger, emoji="❌", custom_id="suggest_no")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_id = interaction.message.id
        user_id = interaction.user.id
        current_vote = await db.has_voted(message_id, user_id)
        
        if current_vote == "no":
            await db.remove_vote(message_id, user_id)
            await interaction.response.send_message("❌ Has quitado tu voto de No", ephemeral=True)
        else:
            await db.add_vote(message_id, user_id, "no")
            await interaction.response.send_message("✅ Has votado No", ephemeral=True)
        
        yes_percentage, no_percentage = await self.calculate_percentages(message_id)
        
        new_view = SuggestionView()
        new_view.yes_button.label = f"Sí ({yes_percentage}%)"
        new_view.no_button.label = f"No ({no_percentage}%)"
        
        thread_url = await db.get_thread_url(message_id)
        if thread_url:
            discussion_button = discord.ui.Button(
                label="Discusión", 
                style=discord.ButtonStyle.link, 
                emoji="💬", 
                url=thread_url
            )
            new_view.add_item(discussion_button)
        
        try:
            await interaction.message.edit(view=new_view)
        except Exception as e:
            print(f"Error actualizando mensaje: {e}")

async def clear_suggestion_data(message_id):
    await db.clear_suggestion_data(message_id)

async def setup(bot):
    bot.add_view(SuggestionView())