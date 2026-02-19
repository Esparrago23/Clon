from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    phone = Column(String(30), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="person")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    person = relationship("Person", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender = Column(String(20))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    content = Column(Text)
    embedding_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    description = Column(Text)
    event_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
