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
from cognitive.persona_state import PersonaStateManager
from cognitive.conversation_state import ConversationState
from cognitive.decision_engine import tomar_decision
from app.domain.models.episode import Episode
from cognitive.web_agent import buscar_en_internet

# ==========================================================
# 👻 MODO AMNESIA 👻
# True: Apaga RAG, perfiles y emociones complejas. 
# Solo prueba la fluidez conversacional humana de Llama 3.
# False: Clona completamente tu cerebro y recuerdos.
# ==========================================================
MODO_AMNESIA = True

rastreador_conversacion = ConversationState()

def generar_respuesta(nombre_chat, remitente_nombre, mensaje_entrante, historial_simulado=None):
    
    # Valores por defecto para el Modo Amnesia
    perfil_social = "Amigo"
    historial = ""
    recuerdos = []
    estado_emocional = "Relajado y casual"
    episodios_pasados = "Ninguno"
    nivel_energia = 5
    
    if not MODO_AMNESIA:
        db = SessionLocal()

        persona = db.query(Person).filter_by(name=remitente_nombre).first()
        if persona:
            perfil_social = f"Relacion: {persona.relationship_type}\nConfianza: {persona.trust_level}/10\nNotas: {persona.profile_notes}"
        else:
            perfil_social = "Amigo de la universidad."

        conversacion = db.query(Conversation).filter_by(name=nombre_chat).first()
        if conversacion:
            mensajes = db.query(Message).filter_by(conversation_id=conversacion.id).order_by(desc(Message.timestamp)).limit(6).all()
            mensajes.reverse()
            lineas = [f"{m.sender_id}: {m.content}" for m in mensajes]
            historial = "\n".join(lineas)
        db.close()

    if historial_simulado:
        historial += "\n" + "\n".join(historial_simulado)

    from cognitive.time_awareness import esta_durmiendo, respuesta_dormido
    
    # 💤 Ciclo de Sueño 💤
    if esta_durmiendo():
        return respuesta_dormido()

    intent = detectar_intencion(mensaje_entrante)
    
    # 🚨 Validar Botón de Pánico 🚨
    if intent == "emergencia":
        return "[ABORT] Emergencia detectada. Requiere intervención humana."
        
    # 👻 Dejar en visto (Ghosting) 👻
    if intent == "fin_conversacion":
        return "[SEEN]"

    # 🎭 Espejeo de Tensión (Tone Mirroring básico) 🎭
    if len(mensaje_entrante) > 150 or "!" in mensaje_entrante:
        tension_delay = True
    else:
        tension_delay = False

    estrategia = seleccionar_estrategia(intent)
    
    rastreador_conversacion.update(intent, mensaje_entrante)
    estado_conversacion = rastreador_conversacion.summary()

    if not MODO_AMNESIA:
        contexto_busqueda = historial + "\n" + remitente_nombre + ": " + mensaje_entrante
        recuerdos = buscar_recuerdos(contexto_busqueda)

        state_manager = PersonaStateManager()
        state_manager.update_time_decay()
        state_manager.update_from_message(mensaje_entrante)
        estado_emocional = state_manager.summary()
        nivel_energia = state_manager.state.energy 
        state_manager.close()

    estrategia_dinamica = tomar_decision(intent, rastreador_conversacion.status, nivel_energia)
    estrategia_combinada = f"Regla Social: {estrategia}\nOrden Táctica: {estrategia_dinamica}"
    
    if not MODO_AMNESIA:
        db_episodes = SessionLocal()
        episodios = db_episodes.query(Episode).filter_by(person_name=remitente_nombre).order_by(desc(Episode.timestamp)).limit(3).all()
        episodios_pasados = "\n".join([f"- {ep.description}" for ep in episodios]) if episodios else "Ningún evento importante reciente."
        db_episodes.close()
    
    # 🌐 Investigador Web (Tool Calling Básico) 🌐
    info_web = ""
    if intent == "investigacion_web":
        if MODO_AMNESIA:
            print(" 🧠 [SHADOW] Web Agent (Amnesia Mode). Formulando query...")
        else:
            print(" 🧠 [SHADOW] Requiere datos del mundo real. Formulando query...")
            
        query_prompt = f"""
Eres un asistente que formula búsquedas de Google. El usuario preguntó esto: '{mensaje_entrante}'
Si pregunta por clima o temperatura y no menciona ciudad, asume que es el lugar local (usa 'clima actual').
Si pregunta por noticias recientes, busca 'noticias principales hoy'.
Devuelve SOLO la frase exacta a buscar en Google, SIN comillas y SIN explicaciones.
"""
        query_resp = ollama.chat(model="llama3", messages=[{"role": "user", "content": query_prompt}])
        query_texto = query_resp["message"]["content"].strip().replace('"', '')
        info_web = buscar_en_internet(query_texto)
        
    print(f" [DEBUG MEMORIA]: {'AMNESIA ACTIVA (Ignorando base de datos)' if MODO_AMNESIA else episodios_pasados}")
    
    prompt = construir_prompt(
        remitente_nombre,
        mensaje_entrante,
        perfil_social,
        historial,
        estrategia_combinada,
        recuerdos,
        estado_emocional,
        estado_conversacion,
        episodios_pasados,
        info_web
    )

    respuesta = ollama.chat(
        model="llama3",
        messages=[{"role": "system", "content": prompt}]
    )

    return respuesta["message"]["content"].strip()