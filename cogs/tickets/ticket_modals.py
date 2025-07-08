import discord
from discord.ext import commands
import asyncio

from config.config import TICKET_CATEGORIES, TICKET_EMOJIS, STAFF_ROLES
from database.database import db

class BaseTicketModal(discord.ui.Modal):
    def __init__(self, category, title):
        super().__init__(title=title)
        self.category = category

    async def create_ticket_channel(self, interaction, form_data):
        try:
            await interaction.response.defer(ephemeral=True)
            
            print(f"Creando ticket para usuario {interaction.user} en categoría {self.category}")
            guild = interaction.guild
            category_id = TICKET_CATEGORIES.get(self.category)
            
            print(f"Categoría {self.category} -> ID {category_id}")
            
            if not category_id:
                await interaction.followup.send("❌ Error: Categoría de ticket no configurada.", ephemeral=True)
                return
                
            category = guild.get_channel(category_id)
            
            if not category:
                await interaction.followup.send("❌ Error: Categoría de tickets no encontrada.", ephemeral=True)
                return

            print(f"Categoría encontrada: {category.name} (ID: {category.id})")

            counter = await db.get_next_ticket_counter(self.category)
            emoji = TICKET_EMOJIS.get(self.category, "🎫")
            channel_name = f"{emoji}{interaction.user.name}-{counter}"
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            
            staff_role_ids = STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]]
            for role_id in staff_role_ids:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

            channel = await category.create_text_channel(
                channel_name,
                overwrites=overwrites
            )
            print(f"Canal creado: {channel.name} en categoría {channel.category.name}")

            await db.create_ticket(
                channel.id, 
                interaction.user.id, 
                self.category, 
                counter,
                form_data
            )

            await channel.send(interaction.user.mention)

            staff_mentions = []
            for role_id in staff_role_ids:
                role = guild.get_role(role_id)
                if role:
                    staff_mentions.append(role.mention)

            embed = discord.Embed(
                title=f"🎫 Ticket de {self.category.replace('_', ' ').title()}",
                color=0x00FF00
            )
            
            for field_name, field_value in form_data.items():
                embed.add_field(name=field_name, value=f"```\n{field_value}\n```", inline=False)

            embed.set_footer(text=f"Ticket creado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

            from .ticket_views import TicketManagementView
            view = TicketManagementView(self.category)
            
            await channel.send(
                content=" ".join(staff_mentions),
                embed=embed,
                view=view
            )

            info_embed = discord.Embed(
                title="ℹ️ Información adicional",
                description="Si tienes más información que proporcionar (coordenadas, evidencias, capturas, etc.), compártela aquí para una atención más rápida.",
                color=0x3498db
            )
            await channel.send(embed=info_embed)

            try:
                from cogs.logs.ticket_logs import log_ticket_creation
                await log_ticket_creation(guild, channel, interaction.user, self.category, form_data)
            except Exception as e:
                print(f"Error en log de creación de ticket: {e}")

            await interaction.followup.send(f"✅ Ticket creado: {channel.mention}", ephemeral=True)
            print(f"Ticket creado exitosamente: {channel.name}")
            
        except Exception as e:
            print(f"Error creando ticket: {e}")
            try:
                await interaction.followup.send("❌ Error al crear el ticket. Inténtalo de nuevo.", ephemeral=True)
            except:
                print(f"No se pudo enviar mensaje de error: {e}")

class SoporteGeneralModal(BaseTicketModal):
    def __init__(self, category):
        super().__init__(category, "Soporte General")
        
        self.username = discord.ui.TextInput(
            label="Nombre de usuario dentro del servidor",
            placeholder="Tu nombre de usuario en Minecraft...",
            required=True,
            max_length=100
        )
        self.modalidad = discord.ui.TextInput(
            label="Modalidad en la que juegas",
            placeholder="Survival, Creative, etc...",
            required=True,
            max_length=100
        )
        self.coordenadas = discord.ui.TextInput(
            label="Coordenadas del problema",
            placeholder="X: 100, Y: 64, Z: 200...",
            required=True,
            max_length=100
        )
        self.problema = discord.ui.TextInput(
            label="Describe tu problema",
            placeholder="Explica detalladamente tu problema...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.username)
        self.add_item(self.modalidad)
        self.add_item(self.coordenadas)
        self.add_item(self.problema)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"SoporteGeneralModal on_submit ejecutado para {interaction.user}")
            form_data = {
                "Nombre de usuario": self.username.value,
                "Modalidad": self.modalidad.value,
                "Coordenadas": self.coordenadas.value,
                "Descripción del problema": self.problema.value
            }
            await self.create_ticket_channel(interaction, form_data)
        except Exception as e:
            print(f"Error en SoporteGeneralModal on_submit: {e}")
            try:
                await interaction.response.send_message("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)

class BugsModal(BaseTicketModal):
    def __init__(self, category):
        super().__init__(category, "Bugs/Problemas Técnicos")
        
        self.username = discord.ui.TextInput(
            label="Nombre de usuario dentro del servidor",
            placeholder="Tu nombre de usuario en Minecraft...",
            required=True,
            max_length=100
        )
        self.modalidad = discord.ui.TextInput(
            label="Modalidad en la que juegas",
            placeholder="Survival, Creative, etc...",
            required=True,
            max_length=100
        )
        self.problema = discord.ui.TextInput(
            label="Describe tu problema",
            placeholder="Explica detalladamente el bug o problema técnico...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.username)
        self.add_item(self.modalidad)
        self.add_item(self.problema)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"BugsModal on_submit ejecutado para {interaction.user}")
            form_data = {
                "Nombre de usuario": self.username.value,
                "Modalidad": self.modalidad.value,
                "Descripción del problema": self.problema.value
            }
            await self.create_ticket_channel(interaction, form_data)
        except Exception as e:
            print(f"Error en BugsModal on_submit: {e}")
            try:
                await interaction.response.send_message("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)

class ComprasModal(BaseTicketModal):
    def __init__(self, category):
        super().__init__(category, "Problemas de Compras")
        
        self.username = discord.ui.TextInput(
            label="Nombre de usuario dentro del servidor",
            placeholder="Tu nombre de usuario en Minecraft...",
            required=True,
            max_length=100
        )
        self.modalidad = discord.ui.TextInput(
            label="Modalidad en la que juegas",
            placeholder="Survival, Creative, etc...",
            required=True,
            max_length=100
        )
        self.id_transferencia = discord.ui.TextInput(
            label="ID de transferencia (la que te llega al correo)",
            placeholder="Introduce el ID de tu transferencia...",
            required=True,
            max_length=100
        )
        self.problema = discord.ui.TextInput(
            label="Describe tu problema",
            placeholder="Explica detalladamente tu problema con la compra...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.username)
        self.add_item(self.modalidad)
        self.add_item(self.id_transferencia)
        self.add_item(self.problema)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"ComprasModal on_submit ejecutado para {interaction.user}")
            form_data = {
                "Nombre de usuario": self.username.value,
                "Modalidad": self.modalidad.value,
                "ID de transferencia": self.id_transferencia.value,
                "Descripción del problema": self.problema.value
            }
            await self.create_ticket_channel(interaction, form_data)
        except Exception as e:
            print(f"Error en ComprasModal on_submit: {e}")
            try:
                await interaction.response.send_message("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)

class ApelacionModal(BaseTicketModal):
    def __init__(self, category):
        super().__init__(category, "Apelación")
        
        self.username = discord.ui.TextInput(
            label="Nombre de usuario dentro del servidor",
            placeholder="Tu nombre de usuario en Minecraft...",
            required=True,
            max_length=100
        )
        self.modalidad = discord.ui.TextInput(
            label="Modalidad en la que juegas",
            placeholder="Survival, Creative, etc...",
            required=True,
            max_length=100
        )
        self.razon_sancion = discord.ui.TextInput(
            label="Razón de tu sanción",
            placeholder="Por qué fuiste sancionado...",
            required=True,
            max_length=200
        )
        self.tiempo_sancion = discord.ui.TextInput(
            label="Tiempo de tu sanción",
            placeholder="Duración de la sanción...",
            required=True,
            max_length=100
        )
        self.argumentos = discord.ui.TextInput(
            label="Escribe tus argumentos para apelar la sanción",
            placeholder="Explica por qué crees que la sanción debería ser removida...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.username)
        self.add_item(self.modalidad)
        self.add_item(self.razon_sancion)
        self.add_item(self.tiempo_sancion)
        self.add_item(self.argumentos)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"ApelacionModal on_submit ejecutado para {interaction.user}")
            form_data = {
                "Nombre de usuario": self.username.value,
                "Modalidad": self.modalidad.value,
                "Razón de la sanción": self.razon_sancion.value,
                "Tiempo de la sanción": self.tiempo_sancion.value,
                "Argumentos de apelación": self.argumentos.value
            }
            await self.create_ticket_channel(interaction, form_data)
        except Exception as e:
            print(f"Error en ApelacionModal on_submit: {e}")
            try:
                await interaction.response.send_message("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)

class ReportarModal(BaseTicketModal):
    def __init__(self, category):
        super().__init__(category, "Reportar a un Jugador")
        
        self.username = discord.ui.TextInput(
            label="Nombre de usuario dentro del servidor",
            placeholder="Tu nombre de usuario en Minecraft...",
            required=True,
            max_length=100
        )
        self.modalidad = discord.ui.TextInput(
            label="Modalidad en la que juegas",
            placeholder="Survival, Creative, etc...",
            required=True,
            max_length=100
        )
        self.jugador_reportado = discord.ui.TextInput(
            label="Nombre del jugador reportado",
            placeholder="Nombre del jugador que quieres reportar...",
            required=True,
            max_length=100
        )
        self.razon_reporte = discord.ui.TextInput(
            label="Describe la razón de tu reporte",
            placeholder="Explica detalladamente por qué reportas a este jugador...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.add_item(self.username)
        self.add_item(self.modalidad)
        self.add_item(self.jugador_reportado)
        self.add_item(self.razon_reporte)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"ReportarModal on_submit ejecutado para {interaction.user}")
            form_data = {
                "Nombre de usuario": self.username.value,
                "Modalidad": self.modalidad.value,
                "Jugador reportado": self.jugador_reportado.value,
                "Razón del reporte": self.razon_reporte.value
            }
            await self.create_ticket_channel(interaction, form_data)
        except Exception as e:
            print(f"Error en ReportarModal on_submit: {e}")
            try:
                await interaction.response.send_message("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Error al procesar el formulario. Inténtalo de nuevo.", ephemeral=True)