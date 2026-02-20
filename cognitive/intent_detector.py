import ollama

def detectar_intencion(mensaje: str) -> str:
    prompt = f"""
Clasifica la intención del siguiente mensaje en UNA sola palabra:

Categorias:
- invitacion
- pregunta
- logistica
- broma
- emocional
- informacion
- saludo
- desconocido

Mensaje:
{mensaje}

Respuesta:
"""

    resp = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return resp["message"]["content"].strip().lower()