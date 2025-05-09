from fastapi.testclient import TestClient
from .main import app
from .database import SessionLocal, engine, Base

# um branco de dados para testes
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"full_name": "Emanuele Vitória", "nickname": "Emanuele", "email": "evjl@gmail.com", "password": "senha123", "gender": "Feminino", "birth_date": "2000-01-01"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Emanuele Vitória"
