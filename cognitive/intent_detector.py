import ollama

def detectar_intencion(mensaje: str) -> str:
    # 🚨 Botón del Pánico Estático 🚨
    # Buscamos palabras clave críticas antes de gastar tokens en el LLM
    palabras_emergencia = ["emergencia", "urgente", "hospital", "accidente", "ayuda", "chocamos", "falleció", "muerto"]
    mensaje_lower = mensaje.lower()
    if any(palabra in mensaje_lower for palabra in palabras_emergencia):
        return "emergencia"

    prompt = f"""
Eres un analizador de intenciones súper estricto. Analiza este mensaje y devuélveme la categoría en formato JSON: {{"intencion": "categoria"}}

REGLAS ESTRICTAS PARA CATEGORÍAS:
"investigacion_web" -> Úsalo SIEMPRE que pidan datos del mundo real: noticias, clima, deportes, dudas de historia, "¿quién ganó?", "¿a cuántos grados...?", política, etc.
"pregunta" -> Úsalo SOLO para preguntas personales ("¿cómo estás?", "¿qué haces?", "¿cómo te fue?"). NUNCA para datos externos.
"emergencia" -> Peligro grave, hospital, ayuda urgente.
"fin_conversacion" -> Despedidas cortas, "jaja", "ok", "bueno".
"invitacion" -> Salidas, planes.
"logistica" -> Coordenadas, horas de verse.
"emocional" -> Tristeza, enojo, alegría.
"broma" -> Chistes, memes, sarcasmo.
"informacion" -> Dando un dato (no preguntando).
"saludo" -> "Hola", "qué onda".
"desconocido" -> Cualquier otra cosa.

Mensaje a clasificar: "{mensaje}"
"""

    resp = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        format="json"
    )

    import json
    try:
        data = json.loads(resp["message"]["content"])
        return data.get("intencion", "desconocido").strip().lower()
    except:
        return "desconocido"