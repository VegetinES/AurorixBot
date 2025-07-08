######################################################
#
#         MODIFICAR ANTES DE EJECUTAR EL BOT
# 
######################################################

# Se tienen que poner las IDs de canales/roles/categorías

WELCOME_CHANNEL_ID = 0 # Canal de bienvenida

STAFF_ROLES = {
    "Staff": [0],  # Roles de Staff (Añadir más IDs separadas por comas: [id1, id2, id3])
    "Admin": 0   # Rol de Admin
}

MUTE_ROLE_ID = 0  # Rol de Muteo

MOD_LOGS_CHANNEL = 0  # Canal de Logs de Moderación
MOD_LOGS_TICKETS_CHANNEL = 0  # Canal de Logs de Tickets

SUGGEST_CHANNEL = 0 # Canal de Sugerencias

TICKETS_CHANNEL = 0  # Canal de Tickets
TICKETS_CATEGORY_BUY = 0  # Categoría de Tickets de compras
TICKETS_CATEGORY_BUGS = 0  # Categoría de Tickets de bugs
TICKETS_CATEGORY_SUPPORT = 0  # Categoría de Tickets de soporte
TICKETS_CATEGORY_APPEAL = 0  # Categoría de Tickets de apelación
TICKETS_CATEGORY_REPORT = 0  # Categoría de Tickets de reportes

TICKET_CATEGORIES = {
    "soporte_general": TICKETS_CATEGORY_SUPPORT,
    "bugs": TICKETS_CATEGORY_BUGS,
    "compras": TICKETS_CATEGORY_BUY,
    "apelacion": TICKETS_CATEGORY_APPEAL,
    "reportar": TICKETS_CATEGORY_REPORT
}

TICKET_EMOJIS = {
    "soporte_general": "🌎",
    "bugs": "🐞",
    "compras": "🛒",
    "apelacion": "⛔",
    "reportar": "⚠️"
}