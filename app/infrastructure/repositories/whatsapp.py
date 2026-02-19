from sqlalchemy.orm import Session
from app.domain.models.person import Person
from app.domain.models.conversation import Conversation
from app.domain.models.message import Message

class WhatsAppRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create_person(self, name: str) -> Person:
        person = self.session.query(Person).filter_by(name=name).first()
        if not person:
            person = Person(name=name)
            self.session.add(person)
            self.session.commit()
            self.session.refresh(person)
        return person

    def get_or_create_conversation(self, name: str, is_group: bool) -> Conversation:
        conv = self.session.query(Conversation).filter_by(name=name).first()
        if not conv:
            conv = Conversation(name=name, is_group=is_group)
            self.session.add(conv)
            self.session.commit()
            self.session.refresh(conv)
        elif is_group and not conv.is_group:
            conv.is_group = True
            self.session.commit()
            self.session.refresh(conv)
        return conv

    def create_message(self, conversation_id, sender_id, whatsapp_id: str, content: str, timestamp) -> Message:
        existing_msg = self.session.query(Message).filter_by(whatsapp_id=whatsapp_id).first()
        if existing_msg:
            return existing_msg
            
        msg = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            whatsapp_id=whatsapp_id,
            content=content,
            timestamp=timestamp
        )
        self.session.add(msg)
        self.session.commit()
        return msg