from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.domain.models.base import BaseModel

class Event(BaseModel):
    __tablename__ = "events"

    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"))
    description = Column(Text)
    event_date = Column(DateTime(timezone=True))

    person = relationship("Person", back_populates="events")