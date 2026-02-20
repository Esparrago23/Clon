import chromadb
from sentence_transformers import SentenceTransformer
from app.core.database import SessionLocal
from app.domain.models.person import Person
from app.domain.models.message import Message

def run_sync():
    print("1. Conectando a la memoria relacional (PostgreSQL)...")
    db = SessionLocal()

    print("2. Conectando al cerebro semántico (ChromaDB)...")
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    
    coleccion = chroma_client.get_or_create_collection(name="personalidad_bug")

    print("3. Cargando modelo neuronal (esto puede tardar la primera vez)...")
    modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    print("4. Buscando tus mensajes...")
    yo = db.query(Person).filter_by(name="Tú").first()
    
    if not yo:
        print("Error: No se encontró al usuario 'Tú' en la BD.")
        return

    mis_mensajes = db.query(Message).filter_by(sender_id=yo.id).all()
    print(f"-> Se encontraron {len(mis_mensajes)} mensajes tuyos en el historial.")

    textos = []
    metadatos = []
    ids = []

    for msg in mis_mensajes:
        if not msg.content or len(msg.content.strip()) < 2:
            continue
            
        textos.append(msg.content)
        metadatos.append({
            "conversation_id": str(msg.conversation_id),
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else ""
        })
        ids.append(str(msg.id))

    if not textos:
        print("No hay textos válidos para procesar.")
        return

    print(f"5. Vectorizando {len(textos)} recuerdos (convirtiendo palabras a matemáticas)...")
    vectores = modelo.encode(textos).tolist()

    print("6. Inyectando vectores en ChromaDB...")
    coleccion.upsert(
        embeddings=vectores,
        documents=textos,
        metadatas=metadatos,
        ids=ids
    )

    print("-" * 50)
    print(" ¡Cerebro semántico sincronizado y listo!")
    
    db.close()

if __name__ == "__main__":
    run_sync()