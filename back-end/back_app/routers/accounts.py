from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importações relativas aos seus módulos (ajuste os caminhos se necessário)
from .. import schemas  # Assume que schemas.py está em back_app/
from .. import models   # Assume que models.py está em back_app/
from ..database import get_session # Para a dependência da sessão do DB
from ..security import get_current_user # Para proteger as rotas

# Cria uma nova instância de APIRouter
router = APIRouter(
    prefix="/accounts",  # Prefixo para todas as rotas neste arquivo
    tags=["accounts"]    # Tag para agrupar na documentação da API (Swagger UI)
)

# Dependência para obter a sessão do banco de dados
# (similar ao que você tem no seu router de /finance)
def get_db():
    db = None
    try:
        db = next(get_session())
        yield db
    finally:
        if db is not None:
            db.close()

# --- Endpoints CRUD para Contas (Accounts) ---

@router.post("/", response_model=schemas.AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(
    account_in: schemas.AccountCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) # Usando models.User aqui
):
    """
    Cria uma nova conta para o usuário autenticado.
    """
    db_account = models.Account(
        name=account_in.name,
        account_type=account_in.account_type,
        icon=account_in.icon,
        balance=account_in.balance,
        user_id=current_user.id  # Associa a conta ao usuário logado
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/", response_model=List[schemas.AccountOut])
def get_accounts(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna todas as contas associadas ao usuário autenticado.
    """
    accounts = db.query(models.Account).filter(models.Account.user_id == current_user.id).all()
    return accounts

@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna uma conta específica pelo ID, se pertencer ao usuário autenticado.
    """
    db_account = db.query(models.Account).filter(
        models.Account.id == account_id, 
        models.Account.user_id == current_user.id
    ).first()
    
    if db_account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada ou não pertence ao usuário")
    return db_account

@router.put("/{account_id}", response_model=schemas.AccountOut)
def update_account(
    account_id: int, 
    account_in: schemas.AccountUpdate, # Usando AccountUpdate para permitir atualizações parciais
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza uma conta existente do usuário autenticado.
    """
    db_account = db.query(models.Account).filter(
        models.Account.id == account_id, 
        models.Account.user_id == current_user.id
    ).first()
    
    if db_account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada ou não pertence ao usuário")
    
    update_data = account_in.model_dump(exclude_unset=True) # Pega apenas os campos enviados para atualização
    for key, value in update_data.items():
        setattr(db_account, key, value)
        
    db.add(db_account) # Adiciona o objeto atualizado à sessão (SQLAlchemy rastreia as mudanças)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/{account_id}", response_model=schemas.Message)
def delete_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    db_account = db.query(models.Account).filter(
        models.Account.id == account_id, 
        models.Account.user_id == current_user.id
    ).first()
    
    if db_account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada ou não pertence ao usuário")
    
    # Considerações adicionais antes de deletar:
    # - O que fazer com transações/despesas/receitas vinculadas a esta conta?
    # - Por agora, apenas deletamos a conta.
    
    db.delete(db_account)
    db.commit()
    return {"message": "Conta deletada com sucesso"}