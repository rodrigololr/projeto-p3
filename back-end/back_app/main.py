from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import auth, users # Importa as rotas existentes

app = FastAPI(title="Projeto P3")

# Monta a pasta 'front-end' para servir arquivos estáticos (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="../front-end"), name="static")

# Inclui as rotas de autenticação, usuários e tarefas
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    # Redireciona para a página principal do front-end
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/html/principal.html")

    # a dependencia do banco de dados
# comentário nao significativo 
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.UserInDB)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.UserInDB)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.UserInDB)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user