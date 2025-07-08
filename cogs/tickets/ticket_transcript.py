import discord
import aiohttp
import base64
from datetime import datetime
import io
import html
import json
import os
import uuid
import mimetypes

async def download_and_save_attachment(url, filename, is_video=False):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                    unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
                    
                    if is_video:
                        file_path = f"att/videos/{unique_filename}"
                        web_path = f"/att/videos/{unique_filename}"
                    else:
                        file_path = f"att/adjuntos/{unique_filename}"
                        web_path = f"/att/adjuntos/{unique_filename}"
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    return web_path
    except Exception as e:
        print(f"Error descargando archivo {filename}: {e}")
    return None

async def create_transcript(channel):
    messages = []
    async for message in channel.history(limit=None, oldest_first=True):
        message_data = await process_message(message)
        messages.append(message_data)
    
    transcript_id = str(uuid.uuid4())
    transcript_data = {
        'transcript_id': transcript_id,
        'channel_info': {
            'name': channel.name,
            'id': channel.id,
            'category': channel.category.name if channel.category else None,
            'guild_name': channel.guild.name,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        },
        'messages': messages
    }
    
    transcript_path = f'transcripciones/{transcript_id}.json'
    with open(transcript_path, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2, default=str)
    
    return transcript_id

async def process_message(message):
    attachments = []
    for attachment in message.attachments:
        content_type = attachment.content_type or 'unknown'
        
        attachment_data = {
            'filename': attachment.filename,
            'url': attachment.url,
            'size': attachment.size,
            'content_type': content_type
        }
        
        if content_type.startswith('image/'):
            attachment_data['is_image'] = True
            attachment_data['is_video'] = False
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as response:
                        if response.status == 200:
                            content = await response.read()
                            attachment_data['base64'] = base64.b64encode(content).decode('utf-8')
            except:
                pass
        elif content_type.startswith('video/'):
            attachment_data['is_image'] = False
            attachment_data['is_video'] = True
            local_path = await download_and_save_attachment(attachment.url, attachment.filename, is_video=True)
            if local_path:
                attachment_data['local_path'] = local_path
        else:
            attachment_data['is_image'] = False
            attachment_data['is_video'] = False
            if attachment.size < 50 * 1024 * 1024:
                local_path = await download_and_save_attachment(attachment.url, attachment.filename, is_video=False)
                if local_path:
                    attachment_data['local_path'] = local_path
        
        attachments.append(attachment_data)

    embeds = []
    for embed in message.embeds:
        embed_data = {
            'title': embed.title,
            'description': embed.description,
            'color': embed.color.value if embed.color else None,
            'url': embed.url,
            'timestamp': embed.timestamp.isoformat() if embed.timestamp else None,
            'footer': {
                'text': embed.footer.text,
                'icon_url': embed.footer.icon_url
            } if embed.footer else None,
            'author': {
                'name': embed.author.name,
                'url': embed.author.url,
                'icon_url': embed.author.icon_url
            } if embed.author else None,
            'thumbnail': {
                'url': embed.thumbnail.url
            } if embed.thumbnail else None,
            'image': {
                'url': embed.image.url
            } if embed.image else None,
            'fields': []
        }
        
        for field in embed.fields:
            embed_data['fields'].append({
                'name': field.name,
                'value': field.value,
                'inline': field.inline
            })
        
        embeds.append(embed_data)

    reactions = []
    for reaction in message.reactions:
        users = []
        async for user in reaction.users():
            users.append({
                'id': user.id,
                'name': user.display_name,
                'avatar': user.display_avatar.url
            })
        
        reactions.append({
            'emoji': str(reaction.emoji),
            'count': reaction.count,
            'users': users
        })

    message_data = {
        'id': message.id,
        'author': {
            'id': message.author.id,
            'name': html.escape(message.author.display_name),
            'username': str(message.author),
            'avatar': message.author.display_avatar.url,
            'bot': message.author.bot
        },
        'content': html.escape(message.content) if message.content else '',
        'timestamp': message.created_at.strftime('%d/%m/%Y %H:%M:%S'),
        'edited_timestamp': message.edited_at.strftime('%d/%m/%Y %H:%M:%S') if message.edited_at else None,
        'attachments': attachments,
        'embeds': embeds,
        'reactions': reactions,
        'pinned': message.pinned,
        'system': message.is_system(),
        'reference': {
            'message_id': message.reference.message_id,
            'channel_id': message.reference.channel_id,
            'guild_id': message.reference.guild_id
        } if message.reference else None
    }
    
    return message_data

def get_transcript_url(transcript_id):
    return f"http://localhost:8080/transcript/{transcript_id}" # Camiar según la configuración del servidor web, la IP y/o el puerto

async def send_transcript_to_user(user, transcript_id, category):
    try:
        transcript_url = get_transcript_url(transcript_id)
        
        embed = discord.Embed(
            title="📋 Transcripción de tu Ticket",
            description=f"Tu ticket de **{category.replace('_', ' ').title()}** ha sido procesado.",
            color=0x00ff00
        )
        embed.add_field(
            name="ℹ️ Información",
            value="Puedes ver la transcripción completa del ticket haciendo clic en el botón de abajo.",
            inline=False
        )
        embed.set_footer(text="Aurorix | Sistema de Tickets")
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Ver Transcripción",
            style=discord.ButtonStyle.link,
            url=transcript_url,
            emoji="📄"
        ))
        
        await user.send(embed=embed, view=view)
    except discord.Forbidden:
        print(f"No se pudo enviar la transcripción a {user.name} - MDs deshabilitados")
    except Exception as e:
        print(f"Error enviando transcripción a {user.name}: {e}")

def get_transcript_button(transcript_id):
    transcript_url = get_transcript_url(transcript_id)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label="Ver Transcripción",
        style=discord.ButtonStyle.link,
        url=transcript_url,
        emoji="📄"
    ))
    return view