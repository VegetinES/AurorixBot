import discord
from discord.ext import commands, tasks
from datetime import datetime

from config.config import MUTE_ROLE_ID
from database.database import db

class ModerationTasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_expired_sanctions.start()

    @tasks.loop(minutes=1)
    async def check_expired_sanctions(self):
        try:
            print("Comprobando usuarios para desmutear y desbanear...")
            
            expired_mutes = await db.get_expired_sanctions(["tempmute"])
            expired_tempbans = await db.get_expired_sanctions(["tempban"])
            
            if expired_mutes:
                print(f"Encontrados {len(expired_mutes)} mutes temporales expirados")
                await self.process_expired_mutes(expired_mutes)
            
            if expired_tempbans:
                print(f"Encontrados {len(expired_tempbans)} bans temporales expirados")
                await self.process_expired_tempbans(expired_tempbans)
            
            if not expired_mutes and not expired_tempbans:
                print("No hay sanciones expiradas para procesar")
                
        except Exception as e:
            print(f"Error al comprobar sanciones expiradas: {e}")

    async def process_expired_mutes(self, expired_mutes):
        for sanction in expired_mutes:
            try:
                user_id = sanction["user_id"]
                sanction_id = sanction["sanction_id"]
                
                guild_found = False
                for guild in self.bot.guilds:
                    member = guild.get_member(user_id)
                    if member:
                        mute_role = guild.get_role(MUTE_ROLE_ID)
                        if mute_role and mute_role in member.roles:
                            await member.remove_roles(mute_role, reason="Mute temporal expirado")
                            print(f"Desmuteo automático aplicado a {member.name} (ID: {user_id})")
                            guild_found = True
                            break
                
                await db.deactivate_sanction(sanction_id)
                
                if not guild_found:
                    print(f"Usuario {user_id} no encontrado en ningún servidor para desmutear")
                    
            except Exception as e:
                print(f"Error procesando mute expirado {sanction['sanction_id']}: {e}")

    async def process_expired_tempbans(self, expired_tempbans):
        for sanction in expired_tempbans:
            try:
                user_id = sanction["user_id"]
                sanction_id = sanction["sanction_id"]
                
                guild_found = False
                for guild in self.bot.guilds:
                    try:
                        user = await self.bot.fetch_user(user_id)
                        if user:
                            ban_entry = await guild.fetch_ban(user)
                            if ban_entry:
                                await guild.unban(user, reason="Ban temporal expirado")
                                print(f"Desbaneo automático aplicado a {user.name} (ID: {user_id})")
                                guild_found = True
                                break
                    except discord.NotFound:
                        continue
                    except Exception as e:
                        print(f"Error verificando ban en {guild.name}: {e}")
                        continue
                
                await db.deactivate_sanction(sanction_id)
                
                if not guild_found:
                    print(f"Usuario {user_id} no encontrado baneado en ningún servidor")
                    
            except Exception as e:
                print(f"Error procesando tempban expirado {sanction['sanction_id']}: {e}")

    @check_expired_sanctions.before_loop
    async def before_check_expired_sanctions(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.check_expired_sanctions.cancel()

async def setup(bot):
    await bot.add_cog(ModerationTasksCog(bot))