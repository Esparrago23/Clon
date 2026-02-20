import json
import os
import hashlib
from datetime import datetime
from app.core.database import SessionLocal
from app.infrastructure.repositories.whatsapp import WhatsAppRepository
from app.application.use_cases.ingest_whatsapp import IngestWhatsAppMessageUseCase

# ==========================================
# MOTOR DE ENLACE DE IDENTIDADES (CROSS-IDENTITY)
# Aquí conectamos el alias de Instagram con el humano real en PostgreSQL
# ==========================================
CHATS_INSTAGRAM = [
    {
        "archivo": "chats/message_1 (1).json",
        "nombre_canonico_bd": "",  # <- EL TRUCO ESTÁ AQUÍ. El nombre exacto que ya tiene en WhatsApp.
        "nombre_instagram": "",    # Cómo se llama en Instagram.
        "mi_usuario_ig": "", # Tu usuario en IG.
        "nombre_chat": "IG Direct - " # La sala separada para no mezclar contextos de plataforma.
    }
]

def decode_meta_string(text):
    # Meta exporta mal los acentos en JSON. Esto repara las 'ñ' y tildes.
    if not text:
        return ""
    try:
        return text.encode('latin1').decode('utf-8')
    except:
        return text

def generate_id(timestamp, sender, text):
    raw = f"{timestamp}{sender}{text}".encode('utf-8')
    return hashlib.md5(raw).hexdigest()

def process_instagram_file(config, use_case):
    filepath = config["archivo"]
    chat_name = config["nombre_chat"]
    nombre_real = config["nombre_canonico_bd"]
    nombre_ig = config["nombre_instagram"]
    mi_ig = config["mi_usuario_ig"]

    if not os.path.exists(filepath):
        print(f" Error: No se encontró {filepath}")
        return 0, 0

    print(f"\nProcesando Instagram: {chat_name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    mensajes_procesados = 0
    mensajes_ignorados = 0

    mensajes_crudos = data.get("messages", [])
    mensajes_crudos.reverse()

    for msg in mensajes_crudos:
        sender_raw = decode_meta_string(msg.get("sender_name", ""))
        content = decode_meta_string(msg.get("content", ""))
        timestamp_ms = msg.get("timestamp_ms", 0)

        basura_meta = ["Enviaste un archivo adjunto.", "Te envió un archivo adjunto.", "Te reaccionó a tu mensaje"]
        if not content or any(basura in content for basura in basura_meta):
            mensajes_ignorados += 1
            continue

        if sender_raw == mi_ig:
            sender = "Tú"
        elif sender_raw == nombre_ig:

            sender = nombre_real 
        else:
            sender = sender_raw 

        timestamp_iso = datetime.fromtimestamp(timestamp_ms / 1000.0).isoformat()

        data_paquete = {
            "id_whatsapp": generate_id(timestamp_iso, sender, content),
            "chat": chat_name,
            "sender": sender,
            "timestamp": timestamp_iso,
            "text": content
        }

        use_case.execute(data_paquete)
        mensajes_procesados += 1

    print(f"Listo: {mensajes_procesados} textos aprendidos | {mensajes_ignorados} multimedia ignorados.")
    return mensajes_procesados, mensajes_ignorados

def run_instagram_ingestion():
    db_session = SessionLocal()
    repo = WhatsAppRepository(db_session)
    use_case = IngestWhatsAppMessageUseCase(repo)

    total_procesados = 0
    total_ignorados = 0

    print("INICIANDO INGESTA CRUZADA DE INSTAGRAM ")
    print("-" * 50)

    for config in CHATS_INSTAGRAM:
        procesados, ignorados = process_instagram_file(config, use_case)
        total_procesados += procesados
        total_ignorados += ignorados

    db_session.close()
    print("-" * 50)
    print("REPORTE FINAL DE INSTAGRAM")
    print(f"Total inyectados en PostgreSQL: {total_procesados}")
    print(f"Total omitidos (Reels/Fotos): {total_ignorados}")

if __name__ == "__main__":
    run_instagram_ingestion()