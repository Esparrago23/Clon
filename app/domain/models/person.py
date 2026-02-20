from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Person(BaseModel):
    __tablename__ = "persons"

    name = Column(String(255), unique=True)
    phone = Column(String(50), nullable=True)
    
    # --- NUEVA CAPA DE INTELIGENCIA SOCIAL ---
    # Ej: "Familia", "Amigo cercano", "Universidad", "Trabajo", "Desconocido"
    relationship_type = Column(String(50), default="Desconocido")
    
    # Del 1 al 10. (1 = Desconocido/Formal, 10 = Mejor amigo/Confianza absoluta)
    trust_level = Column(Integer, default=1) 
    
    # Aquí el LLM irá anotando todo lo que aprenda de esta persona.
    # Ej: "Se llama Pedrito. Estudia derecho. Le gusta el fútbol. Cumple el 5 de mayo."
    profile_notes = Column(Text, default="")
    # ----------------------------------------

    messages_sent = relationship("Message", back_populates="sender_person")
    events = relationship("Event", back_populates="person")
    memories = relationship("Memory", back_populates="person")