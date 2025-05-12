from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from back_app.settings import Settings

engine = create_engine(Settings().DATABASE_URL)

def get_session() -> Session:  # Ajustado pra ser um gerador compatível com FastAPI
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()