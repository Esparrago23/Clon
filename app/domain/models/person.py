from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Person(BaseModel):
    __tablename__ = "persons"

    name = Column(String(255), unique=True) 
    phone = Column(String(50), nullable=True)

    messages_sent = relationship("Message", back_populates="sender_person")
    events = relationship("Event", back_populates="person")
    memories = relationship("Memory", back_populates="person")