from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Conversation(BaseModel):
    __tablename__ = "conversations"

    # Cambiamos a UUID para que coincida con la llave primaria de tu BaseModel
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))

    person = relationship("Person", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")