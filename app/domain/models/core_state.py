from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from app.domain.models.base import BaseModel

class CoreState(BaseModel):
    __tablename__ = "core_states"
    
    name = Column(String(50), unique=True, default="Bug")
    
    energy = Column(Float, default=0.7)
    mood = Column(String(50), default="neutral")
    social_interest = Column(Float, default=0.7)
    cognitive_load = Column(Float, default=0.3)
    
    last_update = Column(DateTime, default=datetime.now)