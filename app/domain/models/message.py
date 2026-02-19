from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    sender_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))
    whatsapp_id = Column(String(100), unique=True, nullable=False)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True))

    conversation = relationship("Conversation", back_populates="messages")
    sender_person = relationship("Person", back_populates="messages_sent")