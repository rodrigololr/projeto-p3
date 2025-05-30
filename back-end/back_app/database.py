from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from back_app.settings import Settings

# Criação do engine
engine = create_engine(Settings().DATABASE_URL)

# Criar a base para os modelos
Base = declarative_base()

# Gerador de sessões para uso no FastAPI
def get_session() -> Session:
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
