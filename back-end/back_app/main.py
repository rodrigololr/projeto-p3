# main.py
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore

from back_app.routers import importCSV
from back_app import database, models
from back_app.database import get_session
from back_app.routers import auth, finance, users
from back_app.routers.finance import initialize_default_goals
from back_app.security import get_password_hash  # <- Importado para hashear a senha

app = FastAPI(title='Projeto P3')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='../front-end'), name='static')

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(finance.router)
app.include_router(importCSV.router)

@app.get('/')
async def root():
    return RedirectResponse(url='/static/html/login.html')

@app.on_event("startup")
async def startup_event():
    with next(get_session()) as db:
        user = db.query(models.User).first()
        if not user:
            hashed_password = get_password_hash("defaultpassword")
            user = models.User(
                username="default_user",
                email="default@example.com",
                password=hashed_password,
                total_balance=0.0
            )
            db.add(user)
            db.commit()
        initialize_default_goals(db, user.id)
