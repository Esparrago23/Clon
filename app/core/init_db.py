from app.core.database import engine
from app.domain.models import Base

def init():
    Base.metadata.create_all(bind=engine)
    print("DB CREATED")

if __name__ == "__main__":
    init()
