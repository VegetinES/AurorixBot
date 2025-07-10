# AurorixBot - Bot de Discord Exclusivo

## Descripción del Proyecto

AurorixBot es un bot de Discord desarrollado exclusivamente para **Aurorix Network** bajo contrato de servicios de desarrollo. Este bot fue creado para gestionar de manera integral el servidor de Discord de la red de servidores de Minecraft Aurorix.

**Servidor de Discord:** https://discord.gg/aurorixx

## Información del Contrato

- **Cliente:** Aurorix Network (Propietarios: caronte7u7 y ymmnl)
- **Tipo de servicio:** Desarrollo de bot de Discord personalizado
- **Estado:** Entregado y en funcionamiento
- **Licencia:** Exclusiva para Aurorix Network

## Características Principales

### 🛡️ Sistema de Moderación Completo
- Comandos de sanción: ban, tempban, kick, mute, tempmute, warn
- Comandos de reversión: unban, unmute, unwarn
- Historial de sanciones por usuario
- Expiración automática de sanciones temporales
- Logs detallados de todas las acciones de moderación

### 🎫 Sistema de Tickets Avanzado
- 5 categorías de tickets: Soporte General, Bugs, Compras, Apelación, Reportes
- Formularios personalizados para cada categoría
- Gestión completa: crear, cerrar, reabrir, eliminar
- Transcripciones automáticas con interfaz web
- Sistema de permisos por roles
- Logs completos de actividad

### 💡 Sistema de Sugerencias
- Votación con porcentajes en tiempo real
- Hilos de discusión automáticos
- Gestión por administradores (aceptar/rechazar/implementado)
- Menús contextuales para gestión rápida

### 👋 Sistema de Bienvenida
- Mensajes personalizados en canal y MD
- Botones interactivos con enlaces importantes
- Contador de miembros dinámico
- Integración con avatares de usuario

### 📊 Comandos Informativos
- Comando IP del servidor
- Enlaces a Discord y tienda
- Información sobre tickets
- Estadísticas de almacenamiento

### 🌐 Servidor Web Integrado
- Visualización de transcripciones de tickets
- Servicio de archivos multimedia
- Interfaz HTML responsive
- Sistema de almacenamiento seguro

### 🗄️ Base de Datos MongoDB
- Gestión de sanciones
- Sistema de tickets
- Votaciones de sugerencias
- Contadores automáticos

### 🧹 Sistema de Limpieza Automática
- Eliminación automática de archivos antiguos
- Gestión de almacenamiento
- Estadísticas de uso

## Estructura del Proyecto

```
AurorixBot/
├── app.py                          # Archivo principal del bot
├── webserver.py                    # Servidor web para transcripciones
├── requirements.txt                # Dependencias del proyecto
├── .gitignore                     # Archivos ignorados por Git
├── config/
│   └── config.py                  # Configuración del bot
├── database/
│   └── database.py                # Conexión y operaciones de MongoDB
├── cogs/
│   ├── commands/                  # Comandos informativos
│   │   ├── discord.py
│   │   ├── ip.py
│   │   ├── ticket.py
│   │   └── tienda.py
│   ├── moderation/                # Sistema de moderación
│   │   ├── ban.py
│   │   ├── kick.py
│   │   ├── mute.py
│   │   ├── warn.py
│   │   ├── unban.py
│   │   ├── unmute.py
│   │   ├── unwarn.py
│   │   ├── sanciones.py
│   │   └── moderation_tasks.py
│   ├── tickets/                   # Sistema de tickets
│   │   ├── ticket_system.py
│   │   ├── ticket_views.py
│   │   ├── ticket_modals.py
│   │   └── ticket_transcript.py
│   ├── suggest/                   # Sistema de sugerencias
│   │   ├── suggest.py
│   │   ├── suggest_buttons.py
│   │   ├── suggest_cmd.py
│   │   └── suggest_context_meny.py
│   ├── logs/                      # Sistema de logs
│   │   ├── mod_logs.py
│   │   └── ticket_logs.py
│   ├── welcome/
│   │   └── welcome.py             # Sistema de bienvenida
│   └── cleanup_system.py          # Sistema de limpieza automática
```

## Comandos Disponibles

### Comandos de Moderación (Staff)
- `/ban <usuario> <razón>` - Banear permanentemente
- `/tempban <usuario> <tiempo> <razón>` - Baneo temporal
- `/kick <usuario> <razón>` - Expulsar usuario
- `/mute <usuario> <razón>` - Silenciar permanentemente
- `/tempmute <usuario> <tiempo> <razón>` - Silencio temporal
- `/warn <usuario> <razón>` - Advertir usuario
- `/unban <usuario> <razón>` - Desbanear usuario
- `/unmute <usuario> <razón>` - Quitar silencio
- `/unwarn <sancion_id>` - Eliminar advertencia
- `/sanciones <usuario>` - Ver historial de sanciones
- `/sugerencia <id> <acción>` - Gestionar sugerencias

### Comandos Informativos (Públicos)
- `!discord` - Información del servidor Discord
- `!ip` - IP del servidor de Minecraft
- `!ticket` - Información sobre tickets
- `!tienda` - Enlace a la tienda

### Comandos de Administración
- `!ticketcreate` - Crear panel de tickets
- `!storage_stats` - Estadísticas de almacenamiento
- `!force_cleanup` - Limpieza forzada de archivos

## Tecnologías Utilizadas

- **Python 3.8+**
- **discord.py 2.5.2** - Librería principal del bot
- **MongoDB** - Base de datos
- **Motor** - Driver asíncrono de MongoDB
- **Flask** - Servidor web para transcripciones
- **aiohttp** - Cliente HTTP asíncrono

## Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- MongoDB
- Token de bot de Discord

### Instalación
1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar `config/config.py` con IDs de canales y roles
4. Configurar variable de entorno `DISCORD_TOKEN_AU`
5. Configurar conexión a MongoDB en `database/database.py`
6. Ejecutar: `python app.py`

## Características Técnicas

### Arquitectura Modular
- Sistema de cogs para organización del código
- Separación de lógica por funcionalidades
- Reutilización de componentes

### Base de Datos
- Esquema optimizado para Discord
- Índices para consultas eficientes
- Respaldo automático de datos

### Servidor Web
- Interfaz HTML para transcripciones
- Sistema de archivos multimedia
- Responsive design

### Seguridad
- Sistema de permisos por roles
- Validación de datos de entrada
- Logs de auditoría completos

## Mantenimiento y Soporte

Este bot fue desarrollado específicamente para Aurorix Network y incluye:
- Documentación completa del código
- Sistema de logs para debugging
- Arquitectura escalable
- Manejo de errores robusto

## Contacto

Bot desarrollado bajo contrato para Aurorix Network como servicio de desarrollo de bots de Discord personalizado.

---

**Nota:** Este repositorio sirve como evidencia del trabajo realizado bajo contrato de servicios de desarrollo para Aurorix Network.