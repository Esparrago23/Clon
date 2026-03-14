from app.core.database import engine
from app.domain.models.base import BaseModel
from app.domain.models.person import Person
from app.domain.models.conversation import Conversation
from app.domain.models.message import Message
from app.domain.models.core_state import CoreState 
from app.domain.models.episode import Episode

def init_db():
    print("Creando tablas en la base de datos...")
    BaseModel.metadata.create_all(bind=engine)
    print("¡Tablas creadas con éxito!")

if __name__ == "__main__":
    init_db()