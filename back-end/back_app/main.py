from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore

# Importa database e models pra inicializar metas
from back_app import database, models
from back_app.database import get_session
# Importa as rotas existentes
from back_app.routers import auth, finance, users, accounts
# Importa a função de inicialização de metasfrom back_app.routers import auth as auth_router
from back_app.routers.finance import initialize_default_goals
from back_app.routers import credit_cards as credit_cards_router
from back_app.routers import accounts as accounts_router  # O NOVO router de contas

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

# Inclui as rotas de autenticação, usuários e finanças
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(finance.router)
app.include_router(accounts_router.router)
app.include_router(credit_cards_router.router)


@app.get('/')
async def root():
    # Redireciona para a página de login do front-end
    return RedirectResponse(url='/static/html/login.html')

# Evento de startup pra inicializar metas padrão


@app.on_event("startup")
async def startup_event():
    with next(get_session()) as db:
        # Busca o primeiro usuário ou cria um se não houver
        user = db.query(models.User).first()
        if not user:
            user = models.User(username="default_user", email="default@example.com",
                               password="defaultpassword", total_balance=0.0)
            db.add(user)
            db.commit()
        initialize_default_goals(db, user.id)
