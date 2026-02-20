from dateutil.parser import isoparse
from app.infrastructure.repositories.whatsapp import WhatsAppRepository

class IngestWhatsAppMessageUseCase:
    def __init__(self, repo: WhatsAppRepository):
        self.repo = repo

    def execute(self, message_data: dict):
        whatsapp_id = str(message_data.get("id_whatsapp"))
        chat_name = message_data.get("chat", "desconocido")
        sender_name = message_data.get("sender", "desconocido")
        content = message_data.get("text", "")
        
        timestamp_str = message_data.get("timestamp")
        timestamp = isoparse(timestamp_str) if timestamp_str else None

        is_group = False
        if sender_name != "Tú" and sender_name != chat_name:
            is_group = True

        conversation = self.repo.get_or_create_conversation(name=chat_name, is_group=is_group)

        person = self.repo.get_or_create_person(name=sender_name)

        self.repo.create_message(
            conversation_id=conversation.id,
            sender_id=person.id,
            whatsapp_id=whatsapp_id,
            content=content,
            timestamp=timestamp
        )
        
        return True