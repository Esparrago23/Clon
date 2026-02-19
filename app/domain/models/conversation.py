from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Conversation(BaseModel):
    __tablename__ = "conversations"

    name = Column(String(255), unique=True) 
    is_group = Column(Boolean, default=False)

    messages = relationship("Message", back_populates="conversation")