from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from app.domain.models.base import BaseModel

class Episode(BaseModel):
    __tablename__ = "episodes"
    
    person_name = Column(String(255), index=True) 

    description = Column(String(500)) 

    emotional_impact = Column(Float, default=0.5) 

    timestamp = Column(DateTime, default=datetime.now)