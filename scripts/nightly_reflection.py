import os
import sys
from datetime import datetime, timedelta
import ollama
import chromadb
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.domain.models.message import Message
from app.domain.models.conversation import Conversation
from app.domain.models.person import Person

def run_reflection():
    print(" 🌙 [NIGHT CACHE] Iniciando ciclo de reflexión nocturna...")
    
    # 1. Obtener mensajes de las últimas 24 horas
    db = SessionLocal()
    hace_24_horas = datetime.now() - timedelta(hours=24)
    
    mensajes_recientes = db.query(Message).filter(Message.timestamp >= hace_24_horas).all()
    
    if not mensajes_recientes:
        print(" 💤 [NIGHT CACHE] No hubo mensajes hoy. Durmiendo...")
        db.close()
        return

    # 2. Agrupar por conversación
    conversaciones = {}
    for m in mensajes_recientes:
        if m.conversation_id not in conversaciones:
            convo = db.query(Conversation).filter_by(id=m.conversation_id).first()
            if convo:
                conversaciones[m.conversation_id] = {"nombre": convo.name, "mensajes": []}
            
        remitente = db.query(Person).filter_by(id=m.sender_id).first()
        nombre_remitente = remitente.name if remitente else "Alguien"
        
        if m.conversation_id in conversaciones:
            conversaciones[m.conversation_id]["mensajes"].append(f"{nombre_remitente}: {m.content}")

    db.close()

    # 3. Inicializar ChromaDB
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    coleccion = chroma_client.get_or_create_collection(name="personalidad_bug")
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # 4. Reflexionar sobre cada conversación y guardar en RAG
    for conv_id, data in conversaciones.items():
        if not data["mensajes"]: continue
        
        historial_texto = "\n".join(data["mensajes"])
        prompt = f"""
El siguiente es un historial de chat de WhatsApp de hoy en el grupo/chat "{data['nombre']}".
Extrae en una o dos oraciones los HECHOS MÁS IMPORTANTES que aprendiste hoy sobre las personas, o sobre ti mismo. Cosas que deberías recordar meses después. Si solo fueron saludos o bromas, responde "NADA IMPORTANTE".

Historial:
{historial_texto[:3000]}

Respuesta (Hechos clave):
"""
        try:
            resp = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
            reflexion = resp["message"]["content"].strip()
            
            if "NADA IMPORTANTE" not in reflexion.upper() and len(reflexion) > 10:
                print(f" 🧠 [NUEVO RECUERDO] {data['nombre']}: {reflexion}")
                
                # Inyectar a ChromaDB
                doc_id = f"memoria_diaria_{datetime.now().strftime('%Y%m%d')}_{conv_id}"
                vector = modelo.encode([reflexion]).tolist()
                
                coleccion.add(
                    embeddings=vector,
                    documents=[reflexion],
                    metadatas=[{"fuente": "reflexion_nocturna", "chat": data['nombre'], "fecha": datetime.now().isoformat()}],
                    ids=[doc_id]
                )
                print(" -> 💾 Memoria guardada a largo plazo (RAG).")
            else:
                 print(f" 🪫 [RUIDO] Chat {data['nombre']} descartado (sin hechos clave).")
        except Exception as e:
            print(f" ❌ [ERROR] Falló la reflexión para el chat {data['nombre']}: {e}")

    print(" 🌅 [NIGHT CACHE] Reflexión nocturna completada. Listo para mañana.")

if __name__ == "__main__":
    run_reflection()
