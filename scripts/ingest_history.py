import os
import re
import hashlib
from datetime import datetime
from app.core.database import SessionLocal
from app.infrastructure.repositories.whatsapp import WhatsAppRepository
from app.application.use_cases.ingest_whatsapp import IngestWhatsAppMessageUseCase
#python -m scripts.ingest_history
# ==========================================
# CONFIGURACIÓN DE PROCESAMIENTO POR LOTES
# Agrega o quita diccionarios según los chats que quieras procesar
# ==========================================
CHATS_A_PROCESAR = [
    {
        "archivo": "chats/.txt", # Ruta del archivo .txt
        "nombre_chat": "",            # Cómo se llamará en la Base de Datos
        "mi_nombre": ""            # Cómo apareces tú en este archivo específico
    },
    {
        "archivo": "chats/Chat de WhatsApp con Trike.txt", # Ruta del archivo .txt
        "nombre_chat": "Trike",            # Cómo se llamará en la Base de Datos
        "mi_nombre": "esparrago"            # Cómo apareces tú en este archivo específico
    },
    {
        "archivo": "chats/Chat de WhatsApp con +52 961 456 5169.txt", # Ruta del archivo .txt
        "nombre_chat": "+52 961 456 5169",            # Cómo se llamará en la Base de Datos
        "mi_nombre": "esparrago"            # Cómo apareces tú en este archivo específico
    },
    {
        "archivo": "chats/Chat de WhatsApp con +52 966 107 0145.txt", # Ruta del archivo .txt
        "nombre_chat": "+52 966 107 0145",            # Cómo se llamará en la Base de Datos
        "mi_nombre": "esparrago"            # Cómo apareces tú en este archivo específico
    },
    {
        "archivo": "chats/Chat de WhatsApp con CHMMAno.txt", # Ruta del archivo .txt
        "nombre_chat": "CHMMAno",            # Cómo se llamará en la Base de Datos
        "mi_nombre": "esparrago"            # Cómo apareces tú en este archivo específico
    },
    # Ejemplo para agregar más:
    # {
    #     "archivo": "chats/grupo_escuela.txt",
    #     "nombre_chat": "Proyecto Final",
    #     "mi_nombre": "Bug"
    # }
]

PATTERN = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s[ap]\.\s?[m]\.)\s-\s(.*)$", re.IGNORECASE)

def clean_time_string(date_str, time_str):
    time_clean = time_str.replace("\u202f", " ").replace(".", "").replace(" ", "").lower()
    time_clean = time_clean.replace("am", " AM").replace("pm", " PM")
    datetime_str = f"{date_str} {time_clean.strip()}"
    try:
        return datetime.strptime(datetime_str, "%d/%m/%Y %I:%M %p").isoformat()
    except:
        return datetime.now().isoformat()

def generate_id(timestamp, sender, text):
    raw = f"{timestamp}{sender}{text}".encode('utf-8')
    return hashlib.md5(raw).hexdigest()

def process_single_file(config, use_case):
    filepath = config["archivo"]
    chat_name = config["nombre_chat"]
    my_name = config["mi_nombre"]

    if not os.path.exists(filepath):
        print(f"Error: No se encontró el archivo {filepath}. Saltando...")
        return 0, 0

    print(f"\nProcesando: {chat_name} ({filepath})...")
    mensajes_procesados = 0
    mensajes_ignorados = 0
    current_msg = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            match = PATTERN.match(line)
            
            if match:
                if current_msg:
                    save_message(current_msg, chat_name, use_case)
                    mensajes_procesados += 1

                date_str = match.group(1)
                time_str = match.group(2)
                rest = match.group(3)

                if ":" not in rest:
                    current_msg = None
                    mensajes_ignorados += 1
                    continue

                sender_raw, text = rest.split(":", 1)
                sender = sender_raw.strip()
                text = text.strip()

                if text == "<Multimedia omitido>":
                    current_msg = None
                    mensajes_ignorados += 1
                    continue
                
                text = text.replace("<Se editó este mensaje.>", "").strip()

                if sender == my_name:
                    sender = "Tú"

                current_msg = {
                    "timestamp": clean_time_string(date_str, time_str),
                    "sender": sender,
                    "text": text
                }
            else:
                if current_msg:
                    current_msg["text"] += f"\n{line.strip()}"

        if current_msg:
            save_message(current_msg, chat_name, use_case)
            mensajes_procesados += 1

    print(f"Listo: {mensajes_procesados} guardados | {mensajes_ignorados} omitidos.")
    return mensajes_procesados, mensajes_ignorados

def save_message(msg_dict, chat_name, use_case):
    data = {
        "id_whatsapp": generate_id(msg_dict["timestamp"], msg_dict["sender"], msg_dict["text"]),
        "chat": chat_name,
        "sender": msg_dict["sender"],
        "timestamp": msg_dict["timestamp"],
        "text": msg_dict["text"]
    }
    use_case.execute(data)

def run_historical_ingestion():
    db_session = SessionLocal()
    repo = WhatsAppRepository(db_session)
    use_case = IngestWhatsAppMessageUseCase(repo)

    total_procesados = 0
    total_ignorados = 0

    print("INICIANDO INGESTA HISTÓRICA POR LOTES ")
    print("-" * 50)

    for config in CHATS_A_PROCESAR:
        procesados, ignorados = process_single_file(config, use_case)
        total_procesados += procesados
        total_ignorados += ignorados

    db_session.close()
    print("-" * 50)
    print("REPORTE FINAL DE INGESTA")
    print(f"Total inyectados en PostgreSQL: {total_procesados}")
    print(f"Total omitidos (sistema/media): {total_ignorados}")

if __name__ == "__main__":
    run_historical_ingestion()