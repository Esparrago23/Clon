from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Person(BaseModel):
    __tablename__ = "persons"

    name = Column(String(100))
    phone = Column(String(30), unique=True)

    conversations = relationship("Conversation", back_populates="person")
    events = relationship("Event", back_populates="person")
    memories = relationship("Memory", back_populates="person")