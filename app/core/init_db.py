from app.core.database import engine
from app.domain.models import Base

def init():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("DB CREATED CORRECTAMENTE")

if __name__ == "__main__":
    init()
