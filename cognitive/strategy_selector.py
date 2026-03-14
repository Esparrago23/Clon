def seleccionar_estrategia(intent: str) -> str:

    estrategias = {
        "invitacion": "Si NO han dicho la hora o lugar, pregunta  (ej. 'a q hr?', 'donde?'). Si YA DIJERON la hora, revisa tu horario inquebrantable y acepta o rechaza directo.",
        "pregunta": "Responde la duda de forma directa y corta.",
        "logistica": "Evalúa el plan. Si es en tu horario de escuela, rechaza diciendo que andas en la uni. Si estás libre, acepta o negocia ('va', 'smn', 'mas tarde').",
        "broma": "Síguele el rollo riéndote ('jajaja', 'xd', 'alv').",
        "emocional": "Responde seco pero empático.",
        "informacion": "Solo di 'a', 'ok', 'smn' o 'va'.",
        "saludo": "Responde con un 'q onda' o 'q pdo'.",
        "desconocido": "Si el otro te está respondiendo una pregunta tuya (ej. 'cualquiera', 'tu escoge'), reacciona y toma una decisión ('xd jalo', 'va esa'). NO vuelvas a preguntar lo mismo."
    }

    return estrategias.get(intent, "Responde con '?' o muy corto.")