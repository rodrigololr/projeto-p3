# back_app/routers/users.py
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime

app = FastAPI()
router = APIRouter()

# negocio de criptografar senhas que o gpt disse que era bom botar sei la tbm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# simula banco de dados
fake_users_db = {
    "user1": {
        "password": "$2b$12$V.uCV0Zvqv8.jWQfgTwnueoPSTw8h0.7Kvg/KLf/MEC6fv89uy/C6"  # "senha123"
    }
}

# atualiza senha 
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@app.put("/api/change-password")
async def change_password(data: PasswordUpdate):
    # if (senha == correta) {"apois ta certo"} else {"ta erradooooo"}
    user_data = fake_users_db.get("user1")  
    if not user_data or not verify_password(data.current_password, user_data["password"]):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    # atualizando a senha com a nova senha (é nada!)
    hashed_new_password = get_password_hash(data.new_password)
    fake_users_db["user1"]["password"] = hashed_new_password
    
    return {"message": "Senha alterada com sucesso!"}

