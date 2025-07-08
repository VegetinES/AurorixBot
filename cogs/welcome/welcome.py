import discord
from discord.ext import commands
import aiohttp

from config.config import WELCOME_CHANNEL_ID

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild # Obtenemos el servidor al que pertenece el usuario
        user_count = guild.member_count # Esto es el parseo del número total de usuarios en el servidor

        # avatar_url se parsea al enlace de la imagen del avatar del usuario
        if member.avatar:
            avatar_url = member.display_avatar.url
        else:
            avatar_url = member.default_avatar.url
        
        # Importante que el json generado en https://discord.builders/ se sustituya null por None, true por True y false por False
        payload_wc = {
            "flags": 1 << 15,
            "components": [ # Aquí es donde se tiene que sustituir el json generado en https://discord.builders/
                {
                    "type": 17,
                    "accent_color": 29951,
                    "spoiler": False,
                    "components": [
                        {
                            "type": 9,
                            "accessory": {
                                "type": 11,
                                "media": {
                                    "url": avatar_url # Aquí se coloca el enlace del avatar del usuario de forma automática al unirse
                                },
                                "description": None,
                                "spoiler": False
                            },
                            "components": [
                                {
                                    "type": 10,
                                    "content": f"\n> ¡Bienvenido/a a **Aurorix** {member.mention}!\n> ({user_count} usuarios)" # member.mention menciona al usuario y user_count muestra el número total de usuarios
                                },
                                {
                                    "type": 10,
                                    "content": "> Disfruta de tu estadía, ¡Estamos está aquí para ayudarte! 😊"
                                }
                            ]
                        },
                        {
                            "type": 14,
                            "divider": True,
                            "spacing": 1
                        },
                        { # Esto son los botones con los enlaces
                            "type": 1,
                            "components": [
                                {
                                    "type": 2,
                                    "style": 5,
                                    "label": "Reglasᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠ",
                                    "emoji": {
                                        "name": "📜",
                                        "id": None
                                    },
                                    "disabled": False,
                                    "url": "https://info.aurorix.online/" # Sustituir por el enlace al canal o web
                                },
                                {
                                    "type": 2,
                                    "style": 5,
                                    "label": "Ticketsᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠ ᅠ ᅠ ᅠᅠᅠᅠ",
                                    "emoji": {
                                        "name": "🎫",
                                        "id": None
                                    },
                                    "disabled": False,
                                    "url": "https://discord.com/channels/824444883745374209/1266658652547190794" # Sustituir por el enlace al canal o web
                                },
                                {
                                    "type": 2,
                                    "style": 5,
                                    "label": "Tiendaᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠ ᅠᅠ ᅠᅠ ᅠᅠ ᅠᅠᅠ",
                                    "emoji": {
                                        "name": "🛒",
                                        "id": None
                                    },
                                    "disabled": False,
                                    "url": "https://tienda.aurorix.online/" # Sustituir por el enlace al canal o web
                                }
                            ]
                        }
                    ]
                }
            ] # que incluye hasta aquí el json generado en https://discord.builders/
        }

        payload_dm = { # Aquí es donde se tiene que sustituir el json generado en https://discord.builders/
            "flags": 1 << 15,
            "components": [
                {
                    "type": 17,
                    "accent_color": 29951,
                    "spoiler": False,
                    "components": [
                        {
                            "type": 9,
                            "accessory": {
                                "type": 11,
                                "media": {
                                    "url": avatar_url
                                },
                                "description": None,
                                "spoiler": False
                            },
                            "components": [
                                {
                                    "type": 10,
                                    "content": f"\n## 🎉 ¡Bienvenido/a {member.name}! 🎉"
                                },
                                {
                                    "type": 10,
                                    "content": "Estamos muy felices de tenerte en nuestro servidor. Aquí tienes algunos detalles importantes para empezar:"
                                }
                            ]
                        },
                        {
                            "type": 10,
                            "content": "🌐 **IP:** `aurorix.online`\n🎮 **Puerto**: `19132`"
                        },
                        {
                            "type": 14,
                            "divider": True,
                            "spacing": 1
                        },
                        {
                            "type": 10,
                            "content": "Además, no olvides echar un vistazo a los siguientes canales importantes:"
                        },
                        {
                            "type": 1,
                            "components": [
                                {
                                    "type": 2,
                                    "style": 5,
                                    "label": "Anunciosㅤ ㅤ ㅤㅤ ㅤ ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ",
                                    "emoji": {
                                        "name": "📢",
                                        "id": None
                                    },
                                    "disabled": False,
                                    "url": "https://discord.com/channels/824444883745374209/1307139902810488943" # Sustituir por el enlace al canal o web
                                },
                                {
                                    "type": 2,
                                    "style": 5,
                                    "label": "Ticketsㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ ㅤ ㅤ ㅤㅤㅤㅤ",
                                    "emoji": {
                                        "name": "🎫",
                                        "id": None
                                    },
                                    "disabled": False,
                                    "url": "https://discord.com/channels/824444883745374209/1266658652547190794" # Sustituir por el enlace al canal o web
                                },
                                {
                                    "type": 2,
                                    "style": 5,
                                    "label": "Tiendaㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ ㅤㅤ ㅤㅤ ㅤㅤ ㅤㅤㅤ",
                                    "emoji": {
                                        "name": "🛒",
                                        "id": None
                                    },
                                    "disabled": False,
                                    "url": "https://tienda.aurorix.online/" # Sustituir por el enlace al canal o web
                                }
                            ]
                        },
                        {
                            "type": 10,
                            "content": "Disfruta de tu estadía, ¡Estamos está aquí para ayudarte! 😊"
                        }
                    ]
                }
            ] # que incluye hasta aquí el json generado en https://discord.builders/
        }

        headers = {
            "Authorization": f"Bot {self.bot.http.token}",
            "Content-Type": "application/json"
        }

        channel_url = f"https://discord.com/api/v10/channels/{WELCOME_CHANNEL_ID}/messages"
        async with self.session.post(channel_url, headers=headers, json=payload_wc) as response:
            if response.status != 200:
                print(f"Error enviando mensaje de bienvenida al canal: {response.status}")

        try:
            dm_channel = await member.create_dm()
            dm_url = f"https://discord.com/api/v10/channels/{dm_channel.id}/messages"
            async with self.session.post(dm_url, headers=headers, json=payload_dm) as dm_response:
                if dm_response.status != 200:
                    print(f"Error enviando mensaje de bienvenida por MD: {dm_response.status}")
        except discord.Forbidden:
            print(f"No se pudo enviar MD a {member.name} - MDs deshabilitados")
        except Exception as e:
            print(f"Error enviando MD a {member.name}: {e}")

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))