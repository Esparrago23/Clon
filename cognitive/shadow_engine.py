import ollama
from sqlalchemy import desc

from app.core.database import SessionLocal
from app.domain.models.person import Person
from app.domain.models.conversation import Conversation
from app.domain.models.message import Message

from cognitive.intent_detector import detectar_intencion
from cognitive.strategy_selector import seleccionar_estrategia
from cognitive.personality_rag import buscar_recuerdos
from cognitive.prompt_builder import construir_prompt


def generar_respuesta(nombre_chat, remitente_nombre, mensaje_entrante):

    db = SessionLocal()

    persona = db.query(Person).filter_by(name=remitente_nombre).first()

    if persona:
        perfil_social = f"""
Relacion: {persona.relationship_type}
Confianza: {persona.trust_level}/10
Notas: {persona.profile_notes}
"""
    else:
        perfil_social = "Persona desconocida"

    conversacion = db.query(Conversation).filter_by(name=nombre_chat).first()

    historial = ""

    if conversacion:
        mensajes = (
            db.query(Message)
            .filter_by(conversation_id=conversacion.id)
            .order_by(desc(Message.timestamp))
            .limit(6)
            .all()
        )

        mensajes.reverse()

        lineas = []

        for m in mensajes:
            lineas.append(f"{m.sender_id}: {m.content}")

        historial = "\n".join(lineas)

    db.close()

    intent = detectar_intencion(mensaje_entrante)

    estrategia = seleccionar_estrategia(intent)

    contexto_busqueda = historial + "\n" + remitente_nombre + ": " + mensaje_entrante
    recuerdos = buscar_recuerdos(contexto_busqueda)

    prompt = construir_prompt(
        remitente_nombre,
        mensaje_entrante,
        perfil_social,
        historial,
        estrategia,
        recuerdos
    )

    respuesta = ollama.chat(
        model="llama3",
        messages=[{"role": "system", "content": prompt}]
    )

    return respuesta["message"]["content"]