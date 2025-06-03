from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import List

from back_app.models import User, Revenue, Expense, Goal
from back_app import database, schemas
from back_app.database import get_session
from back_app.security import get_current_user
import google.generativeai as genai  # type: ignore
import json
import os
import re
from dotenv import load_dotenv  # type: ignore

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API do Gemini
genai.configure(api_key="AIzaSyAgsZ4FJKkGWCm2UjJcHrGVc8xm0zpCdsg")

# Configura o modelo
model = genai.GenerativeModel('gemini-2.0-flash')

router = APIRouter(
    prefix="/finance",
    tags=["finance"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = next(get_session())
    try:
        yield db
    finally:
        db.close()

# Função temporária pra inicializar metas padrão


def initialize_default_goals(db: Session, user_id: int):
    default_goals_data = [
        {"name": "Poupança", "amount": 1000.0,
            "tag": "Poupança", "type": "economia"},
        {"name": "Viagem", "amount": 5000.0, "tag": "Viagem", "type": "economia"},
        {"name": "Casa", "amount": 0.0, "tag": "Casa", "type": "despesa"},
        {"name": "Alimentação", "amount": 0.0,
            "tag": "Alimentação", "type": "despesa"},
        {"name": "Transporte", "amount": 0.0,
            "tag": "Transporte", "type": "despesa"},
        {"name": "Lazer", "amount": 0.0, "tag": "Lazer", "type": "despesa"},
        {"name": "Saúde", "amount": 0.0, "tag": "Saúde", "type": "despesa"},
        {"name": "Educação", "amount": 0.0, "tag": "Educação", "type": "despesa"}
    ]

    existing_goals = db.query(Goal.name).filter(Goal.user_id == user_id).all()
    existing_goal_names = {name_tuple[0] for name_tuple in existing_goals}

    goals_to_add = []
    for g_data in default_goals_data:
        if g_data["name"] not in existing_goal_names:
            goals_to_add.append(Goal(
                name=g_data["name"],
                amount=g_data["amount"],
                user_id=user_id,
                tag=g_data["tag"],
                type=g_data["type"]  # Incluindo o tipo
            ))

    if goals_to_add:
        db.add_all(goals_to_add)
        db.commit()


@router.post("/revenues/", response_model=schemas.RevenueOut)
def create_revenue(
    revenue: schemas.RevenueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_revenue = Revenue(
        name=revenue.name, amount=revenue.amount, user_id=current_user.id)
    db.add(db_revenue)
    db.commit()
    db.refresh(db_revenue)
    current_user.total_balance += revenue.amount
    db.commit()
    return db_revenue


@router.get("/revenues/", response_model=List[schemas.RevenueOut])
def get_revenues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    revenues = db.query(Revenue).filter(
        Revenue.user_id == current_user.id).all()
    return revenues


@router.delete("/revenues/{revenue_id}", response_model=schemas.Message)
def delete_revenue(
    revenue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    revenue = db.query(Revenue).filter(
        Revenue.id == revenue_id,
        Revenue.user_id == current_user.id
    ).first()
    if not revenue:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    current_user.total_balance -= revenue.amount
    db.delete(revenue)
    db.commit()
    return {"message": "Receita deletada com sucesso"}


@router.post("/expenses/", response_model=schemas.ExpenseOut)
def create_expense(
    expense: schemas.ExpenseCreateWithTag,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_expense = Expense(name=expense.name, amount=expense.amount,
                         user_id=current_user.id, tag=expense.tag)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    current_user.total_balance -= expense.amount
    db.commit()
    return db_expense


@router.get("/expenses/", response_model=List[schemas.ExpenseOut])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id).all()
    return expenses


@router.delete("/expenses/{expense_id}", response_model=schemas.Message)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    current_user.total_balance += expense.amount
    db.delete(expense)
    db.commit()
    return {"message": "Despesa deletada com sucesso"}


@router.post("/goals/", response_model=schemas.GoalOut)
def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_goal = Goal(name=goal.name, amount=goal.amount,
                   user_id=current_user.id, tag=goal.tag, type=goal.type)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/goals/", response_model=List[schemas.GoalOut])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    return goals


@router.put("/goals/{goal_id}", response_model=schemas.GoalOut)
def update_goal(
    goal_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db_goal.name = goal.name
    db_goal.amount = goal.amount
    db_goal.tag = goal.tag
    db_goal.type = goal.type
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.delete("/goals/{goal_id}", response_model=schemas.Message)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db.query(Expense).filter(Expense.tag == goal.tag,
                             Expense.user_id == current_user.id).update({"tag": None})
    db.delete(goal)
    db.commit()
    return {"message": "Meta deletada com sucesso"}


@router.get("/balance/", response_model=float)
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return current_user.total_balance


@router.get("/financial-data", response_model=dict)
def get_financial_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    revenues = db.query(Revenue).filter(
        Revenue.user_id == current_user.id).all()
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id).all()
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()

    return {
        "revenues": [{"id": r.id, "name": r.name, "amount": r.amount, "date": r.created_at} for r in revenues],
        "expenses": [{"id": e.id, "name": e.name, "amount": e.amount, "tag": e.tag, "date": e.created_at} for e in expenses],
        "goals": [{"id": g.id, "name": g.name, "amount": g.amount, "tag": g.tag, "type": g.type, "date": g.created_at} for g in goals]
    }


@router.post("/generate-tips", response_model=dict)
def generate_financial_tips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_data = get_financial_data(db=db, current_user=current_user)

    prompt = (
        "Você é um consultor financeiro. Gere 3 dicas financeiras personalizadas com base nos seguintes dados do usuário:\n"
        f"Receitas: {user_data['revenues']}\n"
        
        f"Metas: {user_data['goals']}\n"
        "Cada dica deve ter um título (máximo 30 caracteres) e uma descrição (máximo 100 caracteres). "
        "Retorne as dicas no formato JSON com a estrutura: "
        "{'tips': [{'title': 'Título', 'description': 'Descrição'}, ...]}"
    )

    try:
        response = model.generate_content(prompt)
        # Remove marcações de Markdown (```json e ```)
        cleaned_response = re.sub(r'```json\n|```', '', response.text).strip()
        tips_json = json.loads(cleaned_response)
        return tips_json
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao parsear resposta do Gemini: {str(e)}")
    except Exception as e: 
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar dicas: {str(e)}")
