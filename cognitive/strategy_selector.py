def seleccionar_estrategia(intent: str) -> str:

    estrategias = {
        "invitacion": "mostrar interes pero pedir detalles primero",
        "pregunta": "responder corto y natural",
        "logistica": "responder directo con informacion",
        "broma": "seguir el humor",
        "emocional": "mostrar empatia breve",
        "informacion": "respuesta simple",
        "saludo": "saludo casual corto",
        "desconocido": "respuesta neutral corta"
    }

    return estrategias.get(intent, "respuesta neutral corta")