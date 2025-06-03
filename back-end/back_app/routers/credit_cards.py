from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import List, Optional

# Importações relativas aos seus módulos (ajuste os caminhos se necessário)
from .. import schemas
from .. import models
from ..database import get_session
from ..security import get_current_user

# Cria uma nova instância de APIRouter
router = APIRouter(
    prefix="/creditcards",
    tags=["credit_cards"]
)

# Dependência para obter a sessão do banco de dados


def get_db():
    db = None
    try:
        db = next(get_session())
        yield db
    finally:
        if db is not None:
            db.close()

# --- Endpoints CRUD para Cartões de Crédito (Credit Cards) ---


@router.post("/", response_model=schemas.CreditCardOut, status_code=status.HTTP_201_CREATED)
def create_credit_card(
    credit_card_in: schemas.CreditCardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo cartão de crédito para o usuário autenticado.
    """
    print(
        f"[BACKEND LOG] create_credit_card: Usuário: {current_user.username}, Dados: {credit_card_in.model_dump()}")
    db_credit_card = models.CreditCard(
        name=credit_card_in.name,
        limit=credit_card_in.limit,
        invoice_due_date_str=credit_card_in.invoice_due_date_str,
        icon=credit_card_in.icon,
        user_id=current_user.id
    )
    try:
        db.add(db_credit_card)
        db.commit()
        print(
            f"[BACKEND LOG] create_credit_card: Commit realizado com sucesso para {db_credit_card.name}")
        db.refresh(db_credit_card)
        return db_credit_card
    except Exception as e:
        db.rollback()
        print(f"[BACKEND LOG] create_credit_card: ERRO NO COMMIT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar cartão de crédito no banco: {str(e)}"
        )


@router.get("/", response_model=List[schemas.CreditCardOut])
def get_credit_cards(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna todos os cartões de crédito associados ao usuário autenticado.
    """
    print(
        f"[BACKEND LOG] get_credit_cards: Buscando cartões para Usuário ID: {current_user.id}")
    credit_cards = db.query(models.CreditCard).filter(
        models.CreditCard.user_id == current_user.id).all()
    print(
        f"[BACKEND LOG] get_credit_cards: {len(credit_cards)} cartões encontrados.")
    return credit_cards


@router.get("/{credit_card_id}", response_model=schemas.CreditCardOut)
def get_credit_card(
    credit_card_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna um cartão de crédito específico pelo ID, se pertencer ao usuário autenticado.
    """
    print(
        f"[BACKEND LOG] get_credit_card: Buscando cartão ID: {credit_card_id} para Usuário ID: {current_user.id}")
    db_credit_card = db.query(models.CreditCard).filter(
        models.CreditCard.id == credit_card_id,
        models.CreditCard.user_id == current_user.id
    ).first()

    if db_credit_card is None:
        print(
            f"[BACKEND LOG] get_credit_card: Cartão ID: {credit_card_id} não encontrado para Usuário ID: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cartão de crédito não encontrado ou não pertence ao usuário")
    return db_credit_card


@router.put("/{credit_card_id}", response_model=schemas.CreditCardOut)
def update_credit_card(
    credit_card_id: int,
    credit_card_in: schemas.CreditCardUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza um cartão de crédito existente do usuário autenticado.
    """
    print(
        f"[BACKEND LOG] update_credit_card: Atualizando cartão ID: {credit_card_id} para Usuário ID: {current_user.id}. Dados: {credit_card_in.model_dump(exclude_unset=True)}")
    db_credit_card = db.query(models.CreditCard).filter(
        models.CreditCard.id == credit_card_id,
        models.CreditCard.user_id == current_user.id
    ).first()

    if db_credit_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cartão de crédito não encontrado ou não pertence ao usuário")

    update_data = credit_card_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_credit_card, key, value)

    try:
        db.add(db_credit_card)
        db.commit()
        print(
            f"[BACKEND LOG] update_credit_card: Commit realizado com sucesso para cartão ID: {credit_card_id}")
        db.refresh(db_credit_card)
        return db_credit_card
    except Exception as e:
        db.rollback()
        print(
            f"[BACKEND LOG] update_credit_card: ERRO NO COMMIT para cartão ID {credit_card_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cartão de crédito no banco: {str(e)}"
        )


@router.delete("/{credit_card_id}", response_model=schemas.Message)
def delete_credit_card(
    credit_card_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deleta um cartão de crédito do usuário autenticado.
    """
    print(
        f"[BACKEND LOG] delete_credit_card: Deletando cartão ID: {credit_card_id} para Usuário ID: {current_user.id}")
    db_credit_card = db.query(models.CreditCard).filter(
        models.CreditCard.id == credit_card_id,
        models.CreditCard.user_id == current_user.id
    ).first()

    if db_credit_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cartão de crédito não encontrado ou não pertence ao usuário")

    try:
        db.delete(db_credit_card)
        db.commit()
        print(
            f"[BACKEND LOG] delete_credit_card: Commit realizado com sucesso para deletar cartão ID: {credit_card_id}")
        return {"message": "Cartão de crédito deletado com sucesso"}
    except Exception as e:
        db.rollback()
        print(
            f"[BACKEND LOG] delete_credit_card: ERRO NO COMMIT ao deletar cartão ID {credit_card_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar cartão de crédito no banco: {str(e)}"
        )
