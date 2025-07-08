import discord
from datetime import datetime

from cogs.tickets.ticket_transcript import get_transcript_button
from config.config import MOD_LOGS_TICKETS_CHANNEL

async def log_ticket_creation(guild, channel, creator, category, form_data):
    logs_channel = guild.get_channel(MOD_LOGS_TICKETS_CHANNEL)
    if not logs_channel:
        return

    embed = discord.Embed(
        title="🎫 Ticket Creado",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="Usuario", value=f"{creator.mention} ({creator.id})", inline=True)
    embed.add_field(name="Categoría", value=category.replace('_', ' ').title(), inline=True)
    embed.add_field(name="Canal", value=f"{channel.mention} ({channel.id})", inline=True)
    
    form_text = ""
    for key, value in form_data.items():
        form_text += f"**{key}:** {value}\n"
    
    if form_text:
        embed.add_field(name="Información del formulario", value=form_text[:1024], inline=False)
    
    embed.set_thumbnail(url=creator.display_avatar.url)
    embed.set_footer(text=f"ID del ticket: {channel.id}")
    
    await logs_channel.send(embed=embed)

async def log_ticket_closure(guild, channel, closer, category, transcript_id, close_reason=None):
    logs_channel = guild.get_channel(MOD_LOGS_TICKETS_CHANNEL)
    if not logs_channel:
        return

    embed = discord.Embed(
        title="🔒 Ticket Cerrado",
        color=0xff9900,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="Cerrado por", value=f"{closer.mention} ({closer.id})", inline=True)
    embed.add_field(name="Categoría", value=category.replace('_', ' ').title(), inline=True)
    embed.add_field(name="Canal", value=f"#{channel.name} ({channel.id})", inline=True)
    
    if close_reason:
        embed.add_field(
            name="Razón del cierre",
            value=f"```\n{close_reason}\n```",
            inline=False
        )
    
    embed.add_field(
        name="📋 Transcripción",
        value="La transcripción del ticket está disponible en el enlace de abajo.",
        inline=False
    )
    
    embed.set_thumbnail(url=closer.display_avatar.url)
    embed.set_footer(text=f"ID del ticket: {channel.id}")
    
    await logs_channel.send(embed=embed)

async def log_ticket_reopening(guild, channel, reopener, category):
    logs_channel = guild.get_channel(MOD_LOGS_TICKETS_CHANNEL)
    if not logs_channel:
        return

    embed = discord.Embed(
        title="🔓 Ticket Re-abierto",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="Re-abierto por", value=f"{reopener.mention} ({reopener.id})", inline=True)
    embed.add_field(name="Categoría", value=category.replace('_', ' ').title(), inline=True)
    embed.add_field(name="Canal", value=f"{channel.mention} ({channel.id})", inline=True)
    
    embed.set_thumbnail(url=reopener.display_avatar.url)
    embed.set_footer(text=f"ID del ticket: {channel.id}")
    
    await logs_channel.send(embed=embed)

async def log_ticket_deletion(guild, channel, deleter, transcript_id=None):
    logs_channel = guild.get_channel(MOD_LOGS_TICKETS_CHANNEL)
    if not logs_channel:
        return

    try:
        embed = discord.Embed(
            title="🗑️ Ticket Eliminado",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Eliminado por", value=f"{deleter.mention} ({deleter.id})", inline=True)
        embed.add_field(name="Canal", value=f"#{channel.name} ({channel.id})", inline=True)
        embed.add_field(name="Categoría", value=channel.category.name if channel.category else "Sin categoría", inline=True)
        
        member_count = len([m for m in channel.members if not m.bot])
        embed.add_field(name="Miembros en el ticket", value=str(member_count), inline=True)
        
        message_count = len([msg async for msg in channel.history(limit=None)])
        embed.add_field(name="Total de mensajes", value=str(message_count), inline=True)
        
        embed.set_thumbnail(url=deleter.display_avatar.url)
        embed.set_footer(text=f"ID del ticket: {channel.id}")
        
        if transcript_id:
            embed.add_field(
                name="📋 Transcripción",
                value="La transcripción completa del ticket está disponible en el enlace de abajo.",
                inline=False
            )
            view = get_transcript_button(transcript_id)
            await logs_channel.send(embed=embed, view=view)
        else:
            embed.add_field(
                name="📋 Transcripción",
                value="No hay transcripción disponible para este ticket.",
                inline=False
            )
            await logs_channel.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="🗑️ Ticket Eliminado",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Eliminado por", value=f"{deleter.mention} ({deleter.id})", inline=True)
        embed.add_field(name="Canal", value=f"#{channel.name} ({channel.id})", inline=True)
        embed.add_field(name="Error", value=f"Error en el proceso: {str(e)}", inline=False)
        
        embed.set_thumbnail(url=deleter.display_avatar.url)
        embed.set_footer(text=f"ID del ticket: {channel.id}")
        
        await logs_channel.send(embed=embed)

async def log_user_added_to_ticket(guild, channel, added_user, staff_member):
    logs_channel = guild.get_channel(MOD_LOGS_TICKETS_CHANNEL)
    if not logs_channel:
        return

    embed = discord.Embed(
        title="➕ Usuario Añadido al Ticket",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="Usuario añadido", value=f"{added_user.mention} ({added_user.id})", inline=True)
    embed.add_field(name="Añadido por", value=f"{staff_member.mention} ({staff_member.id})", inline=True)
    embed.add_field(name="Canal", value=f"{channel.mention} ({channel.id})", inline=True)
    
    embed.set_thumbnail(url=added_user.display_avatar.url)
    embed.set_footer(text=f"ID del ticket: {channel.id}")
    
    await logs_channel.send(embed=embed)

async def log_user_removed_from_ticket(guild, channel, removed_user, staff_member):
    logs_channel = guild.get_channel(MOD_LOGS_TICKETS_CHANNEL)
    if not logs_channel:
        return

    embed = discord.Embed(
        title="➖ Usuario Eliminado del Ticket",
        color=0xff9900,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="Usuario eliminado", value=f"{removed_user.mention} ({removed_user.id})", inline=True)
    embed.add_field(name="Eliminado por", value=f"{staff_member.mention} ({staff_member.id})", inline=True)
    embed.add_field(name="Canal", value=f"{channel.mention} ({channel.id})", inline=True)
    
    embed.set_thumbnail(url=removed_user.display_avatar.url)
    embed.set_footer(text=f"ID del ticket: {channel.id}")
    
    await logs_channel.send(embed=embed)