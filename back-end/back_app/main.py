from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore

from .routers import (
    auth,
    finance,
    users,
)  # Importa as rotas existentes e a nova rota finance

app = FastAPI(title='Projeto P3')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # ou use ["http://localhost:8000"] para restringir
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Monta a pasta 'front-end' para servir arquivos estáticos (HTML, CSS, JS)
app.mount('/static', StaticFiles(directory='../front-end'), name='static')

# Inclui as rotas de autenticação, usuários e tarefas
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(finance.router)


@app.get('/')
async def root():
    # Redireciona para a página principal do front-end
    return RedirectResponse(
        url='/static/html/principal.html'
    )  # Ajustado pra principal.html
