from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    sender = Column(String(100))
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True))

    conversation = relationship("Conversation", back_populates="messages")