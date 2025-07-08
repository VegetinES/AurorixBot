import discord
from discord.ext import commands
import aiohttp

class IPCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @commands.command(name='ip')
    async def ip_command(self, ctx):
        url = f"https://discord.com/api/v10/channels/{ctx.channel.id}/messages"
        headers = {
            "Authorization": f"Bot {self.bot.http.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "flags": 1 << 15,
            "components": [
                {
                    "type": 10,
                    "content": "¡¡Recuerda invitar a tus amigos a jugar!!"
                },
                {
                    "type": 17,
                    "accent_color": 29376,
                    "spoiler": False,
                    "components": [
                        {
                            "type": 10,
                            "content": "```ansi\n[2;34m[0m[1;2m[1;34mAurorix[0m | IP: [1;34maurorix.gg[0m | Puerto: [1;34m19132[0m[0m[2;34m[0m```"
                        },
                        {
                            "type": 12,
                            "items": [
                                {
                                    "media": {
                                        "url": "https://api.loohpjames.com/serverbanner.png?ip=aurorix.gg"
                                    },
                                    "description": None,
                                    "spoiler": False
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        async with self.session.post(url, headers=headers, json=payload) as r:
            if r.status != 200:
                print(f"Error enviando respuesta IP: {r.status}")

async def setup(bot):
    await bot.add_cog(IPCommand(bot))