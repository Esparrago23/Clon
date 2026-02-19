import json
import os
from app.core.database import SessionLocal
from app.infrastructure.repositories import WhatsAppRepository
from app.application.use_cases import IngestWhatsAppMessageUseCase

JSONL_FILE = os.path.join(os.path.dirname(__file__), "mensajes_whatsapp.jsonl")

def run_ingestion():
    db_session = SessionLocal()
    
    repo = WhatsAppRepository(db_session)
    use_case = IngestWhatsAppMessageUseCase(repo)

    if not os.path.exists(JSONL_FILE):
        print(f"No se encontró el archivo: {JSONL_FILE}")
        return

    print("Iniciando inyección de memoria al Clon Virtual...")
    contador = 0

    with open(JSONL_FILE, "r", encoding="utf-8") as f:
        for linea in f:
            if not linea.strip():
                continue
            
            try:
                data = json.loads(linea)
                use_case.execute(data)
                contador += 1
                print(f"Memoria inyectada: [{data.get('chat')}] {data.get('sender')} -> {data.get('text')[:30]}...")
            except Exception as e:
                print(f"Error procesando línea: {e}")

    db_session.close()
    print(f"\n¡Proceso completado! Se guardaron {contador} mensajes en PostgreSQL.")

if __name__ == "__main__":
    run_ingestion()