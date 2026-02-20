import chromadb
import ollama
from sentence_transformers import SentenceTransformer

def generar_respuesta_clon(remitente, mensaje_entrante):
    print(f" Mensaje recibido de {remitente}: '{mensaje_entrante}'")
    
    print(" Consultando el cerebro semántico (ChromaDB)...")
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    coleccion = chroma_client.get_collection(name="personalidad_bug")
    modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    vector_query = modelo.encode([mensaje_entrante]).tolist()
    resultados = coleccion.query(
        query_embeddings=vector_query, 
        n_results=5 # Traemos tus 5 mejores respuestas históricas
    )

    recuerdos_texto = "\n".join([f"- {doc}" for doc in resultados['documents'][0]])
    print("\n Recuerdos recuperados (Tu estilo):")
    print(recuerdos_texto)

    system_prompt = f"""Eres un clon digital del usuario llamado "Bug". 
Tu objetivo es responder al mensaje entrante de forma natural y MANTENER LA CONVERSACIÓN FLUYENDO.

REGLAS DE PERSONALIDAD:
1. Actúa como si fueras el humano real. Nunca menciones que eres una IA.
2. Usa estos recuerdos pasados solo como inspiración para tu tono y vocabulario:
{recuerdos_texto}
3. NO tienes que ser obligatoriamente súper corto. Responde con la longitud necesaria para que la conversación tenga sentido y el otro contacto sienta interés.
4. Si te hacen una pregunta directa (ej. "¿vas a ir?"), responde claramente.
5. Usa modismos mexicanos de forma sutil si encajan con el tono de tus recuerdos (ej. "jalo", "chale", "simón"), pero sin exagerar.

OBJETIVO PRINCIPAL:
Lee el mensaje de {remitente}, absorbe el estilo de tus recuerdos, y genera una respuesta que sea coloquial, amistosa y que invite a seguir platicando si es necesario.
"""

    print("\n  Generando respuesta con Llama 3 local...")
    
    respuesta_ia = ollama.chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': system_prompt
        },
        {
            'role': 'user',
            'content': f"El contacto '{remitente}' te acaba de escribir: '{mensaje_entrante}'\n\n¿Qué le respondes?"
        }
    ])

    texto_generado = respuesta_ia['message']['content']
    
    print("-" * 50)
    print(f" RESPUESTA DEL CLON: {texto_generado}")
    print("-" * 50)

if __name__ == "__main__":
    contacto = ""
    mensaje_prueba = "Oye, ¿nos vemos mañana a las 11 am para desayunar?"
    
    generar_respuesta_clon(contacto, mensaje_prueba)