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