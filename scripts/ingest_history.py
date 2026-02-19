import os
import re
import hashlib
from datetime import datetime
from app.core.database import SessionLocal
from app.infrastructure.repositories.whatsapp import WhatsAppRepository
from app.application.use_cases.ingest_whatsapp import IngestWhatsAppMessageUseCase

FILE_PATH = "./chats/.txt" 
CHAT_NAME = ""          
MY_NAME = ""         

PATTERN = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s[ap]\.\s?[m]\.)\s-\s(.*)$", re.IGNORECASE)

def clean_time_string(date_str, time_str):
    time_clean = time_str.replace("\u202f", " ").replace(".", "").replace(" ", "").lower()
    time_clean = time_clean.replace("am", " AM").replace("pm", " PM")
    
    datetime_str = f"{date_str} {time_clean.strip()}"
    try:
        return datetime.strptime(datetime_str, "%d/%m/%Y %I:%M %p").isoformat()
    except Exception as e:
        return datetime.now().isoformat()

def generate_id(timestamp, sender, text):
    raw = f"{timestamp}{sender}{text}".encode('utf-8')
    return hashlib.md5(raw).hexdigest()

def run_historical_ingestion():
    if not os.path.exists(FILE_PATH):
        print(f"Error: No se encontró el archivo {FILE_PATH}")
        return

    db_session = SessionLocal()
    repo = WhatsAppRepository(db_session)
    use_case = IngestWhatsAppMessageUseCase(repo)

    mensajes_procesados = 0
    mensajes_ignorados = 0

    current_msg = None

    print(f"Iniciando lectura masiva de {FILE_PATH}...")

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            match = PATTERN.match(line)
            
            if match:
                if current_msg:
                    save_message(current_msg, use_case)
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

                if sender == MY_NAME:
                    sender = "Tú"

                timestamp = clean_time_string(date_str, time_str)

                current_msg = {
                    "timestamp": timestamp,
                    "sender": sender,
                    "text": text
                }
            else:
                if current_msg:
                    current_msg["text"] += f"\n{line.strip()}"

        if current_msg:
            save_message(current_msg, use_case)
            mensajes_procesados += 1

    db_session.close()
    print("-" * 50)
    print(f" Ingesta Histórica Completa.")
    print(f" Mensajes guardados en PostgreSQL: {mensajes_procesados}")
    print(f" Mensajes omitidos (sistema/multimedia): {mensajes_ignorados}")

def save_message(msg_dict, use_case):
    data = {
        "id_whatsapp": generate_id(msg_dict["timestamp"], msg_dict["sender"], msg_dict["text"]),
        "chat": CHAT_NAME,
        "sender": msg_dict["sender"],
        "timestamp": msg_dict["timestamp"],
        "text": msg_dict["text"]
    }
    use_case.execute(data)

if __name__ == "__main__":
    run_historical_ingestion()