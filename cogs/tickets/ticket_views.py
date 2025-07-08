import discord
from discord.ext import commands
import asyncio

from config.config import TICKET_CATEGORIES, STAFF_ROLES, MOD_LOGS_TICKETS_CHANNEL
from .ticket_transcript import create_transcript, send_transcript_to_user
from database.database import db

class CloseReasonModal(discord.ui.Modal):
    def __init__(self, ticket_category):
        super().__init__(title="Razón de Cierre del Ticket")
        self.ticket_category = ticket_category
        
        self.reason = discord.ui.TextInput(
            label="Razón del cierre",
            placeholder="Explica por qué estás cerrando este ticket...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚠️ ¿Estás seguro de que quieres cerrar este ticket?", view=ConfirmCloseView(self.ticket_category, self.reason.value), ephemeral=True)

class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Elige una categoría para el ticket",
        custom_id="ticket_category_select",
        options=[
            discord.SelectOption(
                label="Soporte general",
                value="soporte_general",
                emoji="🔧",
                description="Para dudas o problemas"
            ),
            discord.SelectOption(
                label="Bugs/Problemas técnicos",
                value="bugs",
                emoji="🪄", 
                description="Para reportar un bug o sugerir"
            ),
            discord.SelectOption(
                label="Problemas de compras",
                value="compras",
                emoji="💵",
                description="Para problemas o dudas sobre comprar un paquete"
            ),
            discord.SelectOption(
                label="Apelación",
                value="apelacion",
                emoji="🛑",
                description="Para apelar una sanción"
            ),
            discord.SelectOption(
                label="Reportar a un jugador",
                value="reportar",
                emoji="🚨",
                description="Para reportar a un jugador"
            )
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            print(f"Usuario {interaction.user} seleccionó categoría: {select.values[0]}")
            category = select.values[0]
            user_id = interaction.user.id

            existing_ticket = await db.get_user_active_ticket(user_id, category)
            if existing_ticket:
                channel = interaction.guild.get_channel(existing_ticket)
                if channel:
                    await interaction.response.send_message(
                        f"❌ Ya tienes un ticket abierto de esta categoría: <#{existing_ticket}>", 
                        ephemeral=True
                    )
                    return
                else:
                    print(f"Canal {existing_ticket} no existe, marcando ticket como eliminado")
                    await db.delete_ticket(existing_ticket)

            from .ticket_modals import (
                SoporteGeneralModal, BugsModal, ComprasModal, 
                ApelacionModal, ReportarModal
            )

            modals = {
                "soporte_general": SoporteGeneralModal,
                "bugs": BugsModal,
                "compras": ComprasModal,
                "apelacion": ApelacionModal,
                "reportar": ReportarModal
            }

            modal = modals[category](category)
            await interaction.response.send_modal(modal)
            print(f"Modal enviado correctamente para categoría: {category}")
            
            select.placeholder = "Elige una categoría para el ticket"
            for option in select.options:
                option.default = False
            
        except Exception as e:
            print(f"Error en category_select: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Error al procesar la selección. Inténtalo de nuevo.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Error al procesar la selección. Inténtalo de nuevo.", ephemeral=True)
            except:
                pass

class TicketManagementView(discord.ui.View):
    def __init__(self, ticket_category):
        super().__init__(timeout=None)
        self.ticket_category = ticket_category

    def has_staff_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        staff_roles = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        return bool(staff_roles.intersection(user_roles))

    def has_admin_permissions(self, member):
        user_roles = {role.id for role in member.roles}
        admin_role_id = STAFF_ROLES["Admin"]
        return admin_role_id in user_roles

    @discord.ui.button(label="Cerrar Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para cerrar tickets.", ephemeral=True)
            return

        if self.ticket_category == "apelacion" and not self.has_admin_permissions(interaction.user):
            await interaction.response.send_message("❌ Solo los administradores pueden cerrar tickets de apelación.", ephemeral=True)
            return

        modal = CloseReasonModal(self.ticket_category)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Añadir Usuario", style=discord.ButtonStyle.secondary, emoji="➕", custom_id="add_user")
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para añadir usuarios.", ephemeral=True)
            return

        await interaction.response.send_message("Selecciona el usuario a añadir:", view=AddUserView(), ephemeral=True)

    @discord.ui.button(label="Eliminar Usuario", style=discord.ButtonStyle.secondary, emoji="➖", custom_id="remove_user")
    async def remove_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ No tienes permisos para eliminar usuarios.", ephemeral=True)
            return

        await interaction.response.send_message("Selecciona el usuario a eliminar:", view=RemoveUserView(), ephemeral=True)

class ConfirmCloseView(discord.ui.View):
    def __init__(self, ticket_category, close_reason):
        super().__init__(timeout=60)
        self.ticket_category = ticket_category
        self.close_reason = close_reason

    @discord.ui.button(label="Sí, cerrar", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        ticket_data = await db.get_ticket_by_channel(channel.id)
        
        if not ticket_data:
            await interaction.response.edit_message(content="❌ Este canal no es un ticket válido.", view=None)
            return

        creator_id, category, users_in_ticket = ticket_data
        
        staff_role_ids = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        
        for member in channel.members:
            if not any(role.id in staff_role_ids for role in member.roles):
                try:
                    await channel.set_permissions(member, view_channel=False)
                except:
                    pass

        transcript_id = await create_transcript(channel)
        await db.update_ticket_status(channel.id, "closed", transcript_id)
        
        embed = discord.Embed(
            title="🔒 Ticket Cerrado",
            description=f"Ticket cerrado por {interaction.user.mention}",
            color=0xFF0000
        )
        
        embed.add_field(
            name="Razón del cierre",
            value=f"```\n{self.close_reason}\n```",
            inline=False
        )
        
        view = TicketClosedView(creator_id, category, users_in_ticket)
        await channel.send(embed=embed, view=view)

        creator = interaction.guild.get_member(creator_id)
        if creator:
            await send_transcript_to_user(creator, transcript_id, category)

        from cogs.logs.ticket_logs import log_ticket_closure
        await log_ticket_closure(interaction.guild, channel, interaction.user, category, transcript_id, self.close_reason)

        await interaction.response.edit_message(content="✅ Ticket cerrado correctamente.", view=None)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Cierre cancelado.", view=None)

class TicketClosedView(discord.ui.View):
    def __init__(self, creator_id, category, users_in_ticket):
        super().__init__(timeout=None)
        self.creator_id = creator_id
        self.category = category
        self.users_in_ticket = users_in_ticket

    @discord.ui.button(label="Eliminar Ticket", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="delete_ticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role_ids = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        if not any(role.id in staff_role_ids for role in interaction.user.roles):
            await interaction.response.send_message("❌ No tienes permisos para eliminar tickets.", ephemeral=True)
            return

        channel = interaction.channel
        
        existing_transcript_id = await db.get_ticket_transcript_id(channel.id)
        
        from cogs.logs.ticket_logs import log_ticket_deletion
        await log_ticket_deletion(interaction.guild, channel, interaction.user, existing_transcript_id)
        
        await db.delete_ticket(channel.id)
        await interaction.response.send_message("🗑️ Eliminando ticket...", ephemeral=True)
        
        await asyncio.sleep(2)
        await channel.delete()

    @discord.ui.button(label="Re-abrir Ticket", style=discord.ButtonStyle.success, emoji="🔓", custom_id="reopen_ticket")
    async def reopen_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role_ids = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        if not any(role.id in staff_role_ids for role in interaction.user.roles):
            await interaction.response.send_message("❌ No tienes permisos para re-abrir tickets.", ephemeral=True)
            return

        channel = interaction.channel
        guild = interaction.guild
        
        for user_id in self.users_in_ticket:
            member = guild.get_member(user_id)
            if member:
                try:
                    await channel.set_permissions(member, view_channel=True, send_messages=True)
                except:
                    pass

        await db.update_ticket_status(channel.id, "open")
        
        embed = discord.Embed(
            title="🔓 Ticket Re-abierto", 
            description=f"Ticket re-abierto por {interaction.user.mention}",
            color=0x00FF00
        )
        
        view = TicketManagementView(self.category)
        
        from cogs.logs.ticket_logs import log_ticket_reopening
        await log_ticket_reopening(guild, channel, interaction.user, self.category)
        
        await interaction.response.edit_message(embed=embed, view=view)

class AddUserView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.select(placeholder="Selecciona usuarios para añadir", cls=discord.ui.UserSelect, custom_id="add_user_select")
    async def add_user_select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        channel = interaction.channel
        added_users = []
        
        for user in select.values:
            try:
                await channel.set_permissions(user, view_channel=True, send_messages=True)
                await db.add_user_to_ticket(channel.id, user.id)
                added_users.append(user.mention)
                
                from cogs.logs.ticket_logs import log_user_added_to_ticket
                await log_user_added_to_ticket(interaction.guild, channel, user, interaction.user)
            except:
                pass
        
        if added_users:
            await interaction.response.edit_message(
                content=f"✅ Usuarios añadidos: {', '.join(added_users)}", 
                view=None
            )
        else:
            await interaction.response.edit_message(
                content="❌ No se pudo añadir ningún usuario.", 
                view=None
            )

class RemoveUserView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.select(placeholder="Selecciona usuarios para eliminar", cls=discord.ui.UserSelect, custom_id="remove_user_select")
    async def remove_user_select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        channel = interaction.channel
        removed_users = []
        
        staff_role_ids = set(STAFF_ROLES["Staff"] + [STAFF_ROLES["Admin"]])
        
        for user in select.values:
            if any(role.id in staff_role_ids for role in user.roles):
                continue
                
            try:
                await channel.set_permissions(user, view_channel=False)
                await db.remove_user_from_ticket(channel.id, user.id)
                removed_users.append(user.mention)
                
                from cogs.logs.ticket_logs import log_user_removed_from_ticket
                await log_user_removed_from_ticket(interaction.guild, channel, user, interaction.user)
            except:
                pass
        
        if removed_users:
            await interaction.response.edit_message(
                content=f"✅ Usuarios eliminados: {', '.join(removed_users)}", 
                view=None
            )
        else:
            await interaction.response.edit_message(
                content="❌ No se pudo eliminar ningún usuario.", 
                view=None
            )