import os
import json
import time
from datetime import datetime, timedelta
import asyncio
import discord
from discord.ext import tasks, commands
from config.config import STAFF_ROLES

class CleanupSystem:
    def __init__(self):
        self.transcript_retention_days = 45 # Días para retener transcripciones
        self.attachment_retention_days = 30 # Días para retener adjuntos
    
    async def cleanup_old_files(self):
        await self.cleanup_transcripts()
        await self.cleanup_attachments()
    
    async def cleanup_transcripts(self):
        try:
            transcripts_dir = 'transcripciones'
            if not os.path.exists(transcripts_dir):
                return
            
            cutoff_date = datetime.now() - timedelta(days=self.transcript_retention_days)
            cleaned_count = 0
            
            for filename in os.listdir(transcripts_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(transcripts_dir, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        generated_at_str = data['channel_info']['generated_at']
                        generated_at = datetime.strptime(generated_at_str, '%d/%m/%Y %H:%M:%S')
                        
                        if generated_at < cutoff_date:
                            os.remove(file_path)
                            cleaned_count += 1
                            print(f"Transcripción eliminada: {filename}")
                    
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        print(f"Error procesando {filename}: {e}")
                        continue
            
            if cleaned_count > 0:
                print(f"Limpieza completada: {cleaned_count} transcripciones eliminadas")
        
        except Exception as e:
            print(f"Error en limpieza de transcripciones: {e}")
    
    async def cleanup_attachments(self):
        try:
            cutoff_time = time.time() - (self.attachment_retention_days * 24 * 60 * 60)
            
            for folder in ['att/videos', 'att/adjuntos']:
                if not os.path.exists(folder):
                    continue
                
                cleaned_count = 0
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    
                    try:
                        file_time = os.path.getmtime(file_path)
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            cleaned_count += 1
                            print(f"Archivo eliminado: {file_path}")
                    except OSError as e:
                        print(f"Error eliminando {file_path}: {e}")
                        continue
                
                if cleaned_count > 0:
                    print(f"Limpieza de {folder}: {cleaned_count} archivos eliminados")
        
        except Exception as e:
            print(f"Error en limpieza de adjuntos: {e}")
    
    def get_storage_stats(self):
        stats = {
            'transcripts': {'count': 0, 'size': 0},
            'videos': {'count': 0, 'size': 0},
            'attachments': {'count': 0, 'size': 0}
        }
        
        if os.path.exists('transcripciones'):
            for filename in os.listdir('transcripciones'):
                if filename.endswith('.json'):
                    file_path = os.path.join('transcripciones', filename)
                    stats['transcripts']['count'] += 1
                    stats['transcripts']['size'] += os.path.getsize(file_path)
        
        if os.path.exists('att/videos'):
            for filename in os.listdir('att/videos'):
                file_path = os.path.join('att/videos', filename)
                stats['videos']['count'] += 1
                stats['videos']['size'] += os.path.getsize(file_path)
        
        if os.path.exists('att/adjuntos'):
            for filename in os.listdir('att/adjuntos'):
                file_path = os.path.join('att/adjuntos', filename)
                stats['attachments']['count'] += 1
                stats['attachments']['size'] += os.path.getsize(file_path)
        
        return stats

class CleanupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_system = CleanupSystem()
        self.cleanup_task.start()
    
    def cog_unload(self):
        self.cleanup_task.cancel()
    
    @tasks.loop(hours=24)
    async def cleanup_task(self):
        await self.cleanup_system.cleanup_old_files()
    
    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        await self.bot.wait_until_ready()
    
    @commands.command(name="storage_stats")
    async def storage_stats(self, ctx):
        if not any(role.id == STAFF_ROLES["Admin"] for role in ctx.author.roles):
            return
        
        stats = self.cleanup_system.get_storage_stats()
        
        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        
        embed = discord.Embed(
            title="📊 Estadísticas de Almacenamiento",
            color=0x3498db
        )
        
        embed.add_field(
            name="📄 Transcripciones",
            value=f"Archivos: {stats['transcripts']['count']}\nTamaño: {format_size(stats['transcripts']['size'])}",
            inline=True
        )
        
        embed.add_field(
            name="🎥 Videos",
            value=f"Archivos: {stats['videos']['count']}\nTamaño: {format_size(stats['videos']['size'])}",
            inline=True
        )
        
        embed.add_field(
            name="📎 Adjuntos",
            value=f"Archivos: {stats['attachments']['count']}\nTamaño: {format_size(stats['attachments']['size'])}",
            inline=True
        )
        
        total_size = stats['transcripts']['size'] + stats['videos']['size'] + stats['attachments']['size']
        total_files = stats['transcripts']['count'] + stats['videos']['count'] + stats['attachments']['count']
        
        embed.add_field(
            name="📈 Total",
            value=f"Archivos: {total_files}\nTamaño: {format_size(total_size)}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="force_cleanup")
    async def force_cleanup(self, ctx):
        if not any(role.id == STAFF_ROLES["Admin"] for role in ctx.author.roles):
            return
        
        await ctx.send("🧹 Iniciando limpieza forzada...")
        await self.cleanup_system.cleanup_old_files()
        await ctx.send("✅ Limpieza completada.")

async def setup(bot):
    await bot.add_cog(CleanupCog(bot))