import discord
from discord.ext import commands, tasks
import os
import glob
import asyncio
import sys
import dotenv

import webserver

from cogs.suggest.suggest_buttons import SuggestionView
from database.database import db

dotenv.load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_AU") # Token del bot de Discord en el archivo .env

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online
    )
    print(f"Estamos dentro! {bot.user}")
    
    try:
        await db.ensure_tables()
        print("Colecciones de base de datos verificadas correctamente")
    except Exception as e:
        print(f"Error verificando colecciones de base de datos: {e}")
    
    try:
        suggestion_view = SuggestionView()
        bot.add_view(suggestion_view)
        print("Vista de sugerencias añadida correctamente")
    except Exception as e:
        print(f"Error añadiendo vista de sugerencias: {e}")
    
    try:
        from cogs.tickets.ticket_views import TicketSelectView, TicketManagementView, TicketClosedView
        
        bot.add_view(TicketSelectView())
        
        for category in ["soporte_general", "bugs", "compras", "apelacion", "reportar"]:
            bot.add_view(TicketManagementView(category))
        
        bot.add_view(TicketClosedView(None, None, []))
        
        print("Vistas de tickets añadidas correctamente")
    except Exception as e:
        print(f"Error añadiendo vistas de tickets: {e}")
    
    print("Cargando extensiones...")
    
    await load_extensions(["cogs"])
    
    try:
        await bot.tree.sync()
        print("Slash commands sincronizados correctamente")
    except Exception as e:
        print(f"Error sincronizando slash commands: {e}")

async def load_extensions(directories):
    total_extensions = 0
    main_extensions = 0
    subdir_extensions = 0
    
    excluded_files = [
        "cogs/tickets/ticket_transcript.py",
        "cogs/tickets/ticket_modals.py"
    ]
    
    for directory in directories:
        main_files = [f for f in glob.glob(f"{directory}/*.py") 
                     if "__pycache__" not in f and f not in excluded_files]
        
        subdir_files = [f for f in glob.glob(f"{directory}/**/*.py", recursive=True) 
                       if "__pycache__" not in f and f not in excluded_files]
        
        subdir_files = [f for f in subdir_files if f not in main_files]
        
        all_files = main_files + subdir_files
        
        for file in all_files:
            if file.endswith(".py"):
                extension = file[:-3].replace("\\", ".").replace("/", ".")
                
                try:
                    await bot.load_extension(extension)
                    print(f"Extensión cargada: {extension}")
                    total_extensions += 1
                    if file in main_files:
                        main_extensions += 1
                    else:
                        subdir_extensions += 1
                except Exception as e:
                    print(f"Error cargando {extension}: {e}")
    
    print(f"\nTotal de extensiones cargadas: {total_extensions}")
    print(f"Extensiones en directorios principales: {main_extensions}")
    print(f"Extensiones en subdirectorios: {subdir_extensions}")

async def main():
    try:
        print("Iniciando proceso principal...")
        print(f"Python version: {sys.version}")
        print(f"Discord.py version: {discord.__version__}")

        print("Iniciando bot de Discord...")
        try:
            await bot.start(DISCORD_TOKEN)
        except discord.LoginFailure as e:
            print(f"Error de login: {e}")
        except Exception as e:
            print(f"Error inesperado: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"Error en main: {type(e).__name__}: {e}")
    finally:
        if db.client:
            db.client.close()

if __name__ == "__main__":
    print("Iniciando servidor web...")
    web_thread = webserver.keep_alive()
    print("Servidor web iniciado en segundo plano")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Cerrando por interrupción del usuario...")
    except Exception as e:
        print(f"Error crítico: {type(e).__name__}: {e}")
    finally:
        loop.close()