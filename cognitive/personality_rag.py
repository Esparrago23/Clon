import chromadb
from sentence_transformers import SentenceTransformer

modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def buscar_recuerdos(texto: str, n=4):

    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    coleccion = chroma_client.get_collection(name="personalidad_bug")

    vector = modelo.encode([texto]).tolist()

    resultados = coleccion.query(
        query_embeddings=vector,
        n_results=n
    )

    return resultados["documents"][0]