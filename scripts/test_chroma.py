import chromadb
from sentence_transformers import SentenceTransformer

def test_memoria():
    print("Conectando al cerebro...")
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    coleccion = chroma_client.get_collection(name="personalidad_bug")
    modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # ---> CAMBIA ESTA FRASE POR LO QUE QUIERAS PROBAR <---
    pregunta_simulada = "¿Qué onda, vamos a comer o qué?"
    
    print(f"\nBuscando en tu memoria cómo sueles hablar sobre: '{pregunta_simulada}'\n")
    
    # Convertimos la pregunta en matemáticas y buscamos los 3 recuerdos más parecidos
    vector_query = modelo.encode([pregunta_simulada]).tolist()
    resultados = coleccion.query(
        query_embeddings=vector_query, 
        n_results=3 # Queremos tus top 3 respuestas más probables
    )

    for i, doc in enumerate(resultados['documents'][0]):
        distancia = resultados['distances'][0][i]
        print(f"Recuerdo {i+1} (Distancia: {distancia:.4f}): {doc}")

if __name__ == "__main__":
    test_memoria()