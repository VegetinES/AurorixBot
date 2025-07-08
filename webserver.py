from flask import Flask, render_template_string, send_from_directory, abort
from threading import Thread
import logging
import os
import json

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('', template_folder='web')

if not os.path.exists('att'):
    os.makedirs('att')
if not os.path.exists('att/videos'):
    os.makedirs('att/videos')
if not os.path.exists('att/adjuntos'):
    os.makedirs('att/adjuntos')
if not os.path.exists('transcripciones'):
    os.makedirs('transcripciones')

@app.route('/')
def index():
    return "Aurorix Bot Server - Sistema de Transcripciones"

@app.route('/transcript/<transcript_id>')
def view_transcript(transcript_id):
    try:
        transcript_path = f'transcripciones/{transcript_id}.json'
        if not os.path.exists(transcript_path):
            abort(404)
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        html_content = generate_html_from_data(data)
        return html_content
    except Exception as e:
        abort(500)

@app.route('/att/videos/<filename>')
def serve_video(filename):
    try:
        return send_from_directory('att/videos', filename)
    except:
        abort(404)

@app.route('/att/adjuntos/<filename>')
def serve_attachment(filename):
    try:
        return send_from_directory('att/adjuntos', filename)
    except:
        abort(404)

def generate_html_from_data(data):
    channel_info = data['channel_info']
    messages = data['messages']
    
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcripción - {channel_info['name']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #36393f;
            color: #dcddde;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #2f3136;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        .header {{
            background-color: #5865f2;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            color: white;
            font-size: 24px;
        }}
        .info {{
            background-color: #40444b;
            padding: 15px 20px;
            border-bottom: 1px solid #4f545c;
        }}
        .message {{
            padding: 15px 20px;
            border-bottom: 1px solid #40444b;
            display: flex;
            gap: 15px;
        }}
        .message:hover {{
            background-color: #32353b;
        }}
        .avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .message-content {{
            flex: 1;
        }}
        .message-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 5px;
        }}
        .username {{
            font-weight: 600;
            color: #ffffff;
        }}
        .bot-tag {{
            background-color: #5865f2;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
        }}
        .timestamp {{
            color: #72767d;
            font-size: 12px;
        }}
        .message-text {{
            margin: 5px 0;
            word-wrap: break-word;
        }}
        .embed {{
            border-left: 4px solid #5865f2;
            background-color: #2f3136;
            margin: 10px 0;
            border-radius: 4px;
            overflow: hidden;
        }}
        .embed-content {{
            padding: 15px;
        }}
        .embed-title {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #00b0f4;
        }}
        .embed-description {{
            margin-bottom: 10px;
        }}
        .embed-field {{
            margin-bottom: 10px;
        }}
        .embed-field-name {{
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .embed-footer {{
            color: #72767d;
            font-size: 12px;
            margin-top: 10px;
        }}
        .attachment {{
            background-color: #40444b;
            border: 1px solid #4f545c;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
        }}
        .attachment-image {{
            max-width: 400px;
            max-height: 300px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .attachment-video {{
            max-width: 500px;
            max-height: 400px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .attachment-file {{
            background-color: #36393f;
            border: 1px solid #4f545c;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            text-decoration: none;
            color: #dcddde;
            display: inline-block;
        }}
        .attachment-file:hover {{
            background-color: #40444b;
        }}
        .reactions {{
            display: flex;
            gap: 5px;
            margin-top: 10px;
            flex-wrap: wrap;
        }}
        .reaction {{
            background-color: #40444b;
            border: 1px solid #4f545c;
            border-radius: 12px;
            padding: 4px 8px;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .system-message {{
            background-color: #5865f2;
            color: white;
            text-align: center;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-style: italic;
        }}
        .edited {{
            color: #72767d;
            font-size: 10px;
            margin-left: 5px;
        }}
        .reply {{
            border-left: 3px solid #4f545c;
            padding-left: 10px;
            margin-bottom: 10px;
            background-color: rgba(79, 84, 92, 0.3);
        }}
        pre {{
            background-color: #2f3136;
            border: 1px solid #40444b;
            border-radius: 4px;
            padding: 10px;
            overflow-x: auto;
        }}
        code {{
            background-color: #2f3136;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Transcripción del Ticket</h1>
        </div>
        <div class="info">
            <strong>Canal:</strong> #{channel_info['name']}<br>
            <strong>Categoría:</strong> {channel_info.get('category', 'Sin categoría')}<br>
            <strong>Servidor:</strong> {channel_info['guild_name']}<br>
            <strong>Fecha de generación:</strong> {channel_info['generated_at']}<br>
            <strong>Total de mensajes:</strong> {len(messages)}
        </div>
        <div class="messages">
"""

    for message in messages:
        if message.get('system', False):
            html_template += f"""
            <div class="system-message">
                {message['content']}
            </div>
"""
            continue

        html_template += f"""
        <div class="message" id="message-{message['id']}">
            <img class="avatar" src="{message['author']['avatar']}" alt="Avatar">
            <div class="message-content">
                <div class="message-header">
                    <span class="username">{message['author']['name']}</span>
                    {f'<span class="bot-tag">BOT</span>' if message['author']['bot'] else ''}
                    <span class="timestamp">{message['timestamp']}</span>
                    {f'<span class="edited">(editado)</span>' if message.get('edited_timestamp') else ''}
                </div>
"""

        if message.get('reference'):
            html_template += f"""
                <div class="reply">
                    Respondiendo al mensaje ID: {message['reference']['message_id']}
                </div>
"""

        if message.get('content'):
            content = message['content'].replace('<', '&lt;').replace('>', '&gt;')
            html_template += f"""
                <div class="message-text">{content}</div>
"""

        for embed in message.get('embeds', []):
            color = f"border-left-color: #{embed['color']:06x};" if embed.get('color') else ""
            html_template += f"""
                <div class="embed" style="{color}">
                    <div class="embed-content">
"""
            if embed.get('title'):
                html_template += f'<div class="embed-title">{embed["title"]}</div>'
            if embed.get('description'):
                html_template += f'<div class="embed-description">{embed["description"]}</div>'
            
            for field in embed.get('fields', []):
                html_template += f"""
                        <div class="embed-field">
                            <div class="embed-field-name">{field['name']}</div>
                            <div>{field['value']}</div>
                        </div>
"""
            
            if embed.get('footer'):
                html_template += f'<div class="embed-footer">{embed["footer"]["text"]}</div>'
            
            html_template += """
                    </div>
                </div>
"""

        for attachment in message.get('attachments', []):
            html_template += f"""
                <div class="attachment">
                    <strong>📎 {attachment['filename']}</strong>
                    <br>Tamaño: {attachment['size']} bytes
                    <br>Tipo: {attachment['content_type']}
"""
            if attachment['is_image'] and attachment.get('base64'):
                html_template += f"""
                    <br><img class="attachment-image" src="data:{attachment['content_type']};base64,{attachment['base64']}" alt="{attachment['filename']}">
"""
            elif attachment.get('local_path'):
                if attachment.get('is_video'):
                    html_template += f"""
                    <br><video class="attachment-video" controls>
                        <source src="{attachment['local_path']}" type="{attachment['content_type']}">
                        Tu navegador no soporta la reproducción de video.
                    </video>
"""
                else:
                    html_template += f"""
                    <br><a class="attachment-file" href="{attachment['local_path']}" target="_blank">
                        📄 Descargar {attachment['filename']}
                    </a>
"""
            html_template += """
                </div>
"""

        if message.get('reactions'):
            html_template += """
                <div class="reactions">
"""
            for reaction in message['reactions']:
                html_template += f"""
                    <div class="reaction">
                        <span>{reaction['emoji']}</span>
                        <span>{reaction['count']}</span>
                    </div>
"""
            html_template += """
                </div>
"""

        html_template += """
            </div>
        </div>
"""

    html_template += """
        </div>
    </div>
</body>
</html>
"""
    
    return html_template

def run():
    app.run(host='0.0.0.0', port=8080, debug=False) # El puerto es necesario que esté abierto en el firewall del servidor

def keep_alive():
    server = Thread(target=run, daemon=True)
    server.start()
    return server