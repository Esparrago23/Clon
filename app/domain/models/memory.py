from sqlalchemy import Column, Text, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Memory(BaseModel):
    __tablename__ = "memories"

    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))
    content = Column(Text)
    embedding_id = Column(String(100)) # Aquí irá el ID de ChromaDB

    person = relationship("Person", back_populates="memories")