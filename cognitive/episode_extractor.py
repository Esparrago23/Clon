import ollama
import json
import re
from sqlalchemy import desc
from app.core.database import SessionLocal
from app.domain.models.conversation import Conversation
from app.domain.models.message import Message
from app.domain.models.episode import Episode

class EpisodeExtractor:
    def __init__(self):
        self.db = SessionLocal()

    def extraer_de_historial(self, nombre_chat, limite_mensajes=12):
        """Busca en la BD la charla reciente y extrae el episodio"""
        conversacion = self.db.query(Conversation).filter_by(name=nombre_chat).first()
        if not conversacion:
            print(f"No se encontró la conversación: {nombre_chat}")
            return
            
        mensajes = self.db.query(Message).filter_by(conversation_id=conversacion.id).order_by(desc(Message.timestamp)).limit(limite_mensajes).all()
        mensajes.reverse()
        
        if not mensajes:
            return

        transcript = "\n".join([f"{m.sender}: {m.content}" for m in mensajes])
        self._procesar_y_guardar(nombre_chat, transcript)

    def extraer_de_texto(self, nombre_chat, transcript_texto):
        """Función rápida para pruebas manuales con texto directo"""
        self._procesar_y_guardar(nombre_chat, transcript_texto)

    def _procesar_y_guardar(self, nombre_chat, transcript):
        prompt = f"""Eres el subconsciente lógico de Bug. Analiza la siguiente conversación y decide si ocurrió un EVENTO IMPORTANTE que valga la pena recordar a largo plazo.

EVENTOS IMPORTANTES (Devolver true):
- Acuerdos de planes, fechas, horas o lugares (Ej. "Vamos al cine a las 10").
- Noticias impactantes, problemas graves o chismes (Ej. "Reprobé el examen", "Me peleé").
- Deudas o favores (Ej. "Te debo 50 pesos").

CHARLA TRIVIAL (Devolver OBLIGATORIAMENTE false):
- Saludos ("q onda", "hola").
- Preguntas de estado actual ("q haces", "aqui viendo yt", "nada").
- Memes, risas cortas o respuestas como "xd", "a", "smn" sin contexto de un plan.

Conversación reciente:
{transcript}

REGLAS:
1. Si la charla es trivial, DEBES poner "evento_detectado": false. ¡NO INVENTES EVENTOS!
2. Usa SOLO el formato JSON exacto que se muestra abajo.

Formato esperado:
{{"evento_detectado": true/false, "descripcion": "Resumen en 3ra persona (solo si es true). Si es false, pon 'Ninguno'.", "impacto_emocional": 0.5}}
"""
        print(" Analizando la charla en busca de recuerdos a largo plazo...")
        
        try:
            respuesta = ollama.chat(
                model="llama3",
                messages=[{"role": "system", "content": prompt}]
            )
            
            texto_crudo = respuesta["message"]["content"]
            match = re.search(r'\{.*\}', texto_crudo, re.DOTALL)
            
            if match:
                datos = json.loads(match.group(0))
                
                # Forzamos una doble verificación por si Llama 3 es terco
                if datos.get("evento_detectado") is True and datos.get("descripcion") != "Ninguno":
                    nuevo_episodio = Episode(
                        person_name=nombre_chat,
                        description=datos["descripcion"],
                        emotional_impact=datos.get("impacto_emocional", 0.5)
                    )
                    self.db.add(nuevo_episodio)
                    self.db.commit()
                    print(f" ¡NUEVO RECUERDO GUARDADO! -> {datos['descripcion']}")
                else:
                    print(" Charla trivial. Nada importante que recordar.")
            else:
                print(" Llama 3 no devolvió un JSON válido.")
                print(f"Texto crudo devuelto: {texto_crudo}")
                
        except Exception as e:
            print(f" Error en la extracción: {e}")

    def close(self):
        self.db.close()

if __name__ == "__main__":
    extractor = EpisodeExtractor()
    
    print("-" * 50)
    print(" PRUEBA 1: Charla Trivial")
    charla_aburrida = """
Roy: q onda we
Bug: q pdo
Roy: q haces
Bug: nada we viendo yt
Roy: a xd
    """
    extractor.extraer_de_texto("Roy", charla_aburrida)
    
    print("\n" + "-" * 50)
    print(" PRUEBA 2: Evento Importante")
    charla_importante = """
Trike: weyyy reprobé el examen del doc carlos :(
Bug: no mames alv we
Trike: sigo llorando de la rabia
Bug: chale, te toca recursar en verano ni pedo
    """
    extractor.extraer_de_texto("Trike", charla_importante)
    
    extractor.close()