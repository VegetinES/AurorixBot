import discord
from datetime import datetime
from config.config import MOD_LOGS_CHANNEL

async def log_sanction(guild, user, moderator, sanction_type, reason):
    logs_channel = guild.get_channel(MOD_LOGS_CHANNEL)
    if not logs_channel:
        return

    timestamp = int(datetime.now().timestamp())
    
    embed = discord.Embed(
        title=f"Sanción aplicada ({sanction_type})",
        color=0xff0000
    )
    
    embed.add_field(
        name="Sancionado",
        value=f"{user.mention} (`{user.id}`)",
        inline=True
    )
    
    embed.add_field(
        name="Moderador", 
        value=f"{moderator.mention} (`{moderator.id}`)",
        inline=True
    )
    
    embed.add_field(
        name="Fecha de la sanción",
        value=f"<t:{timestamp}:F> (<t:{timestamp}:R>)",
        inline=True
    )
    
    embed.add_field(
        name="Razón",
        value=reason,
        inline=False
    )
    
    embed.set_image(url="https://i.imgur.com/Bm36cjv.png")
    
    await logs_channel.send(embed=embed)

async def log_removal_sanction(guild, user, moderator, sanction_type, reason):
    logs_channel = guild.get_channel(MOD_LOGS_CHANNEL)
    if not logs_channel:
        return
    
    embed = discord.Embed(
        title=f"Sanción des-aplicada ({sanction_type}) en Aurorix",
        color=1900288
    )
    
    embed.add_field(
        name="Sancionado",
        value=f"{user.mention} (`{user.id}`)",
        inline=True
    )
    
    embed.add_field(
        name="Moderador", 
        value=f"{moderator.mention} (`{moderator.id}`)",
        inline=True
    )
    
    embed.add_field(
        name="Razón",
        value=reason,
        inline=False
    )
    
    embed.set_image(url="https://i.imgur.com/9webzF5.png")
    
    await logs_channel.send(embed=embed)

async def send_dm_sanction(user, sanction_type, reason):
    try:
        embed = discord.Embed(
            title=f"Sanción aplicada ({sanction_type}) en Aurorix",
            color=0xff0000
        )
        
        embed.add_field(
            name="Razón",
            value=reason,
            inline=False
        )
        
        embed.set_image(url="https://i.imgur.com/Bm36cjv.png")
        
        await user.send(embed=embed)
    except discord.Forbidden:
        print(f"No se pudo enviar MD a {user.name} - MDs deshabilitados")
    except Exception as e:
        print(f"Error enviando MD a {user.name}: {e}")

async def send_dm_removal_sanction(user, sanction_type, reason):
    try:
        embed = discord.Embed(
            title=f"Sanción des-aplicada ({sanction_type}) en Aurorix",
            color=1900288
        )
        
        embed.add_field(
            name="Razón",
            value=reason,
            inline=False
        )
        
        embed.set_image(url="https://i.imgur.com/9webzF5.png")
        
        await user.send(embed=embed)
    except discord.Forbidden:
        print(f"No se pudo enviar MD a {user.name} - MDs deshabilitados")
    except Exception as e:
        print(f"Error enviando MD a {user.name}: {e}")