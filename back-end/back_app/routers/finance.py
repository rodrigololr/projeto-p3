from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from back_app import database, models, schemas
from back_app.database import get_session
from back_app.security import get_current_user

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
    default_goals = [
        models.Goal(name="Poupança", amount=1000.0, user_id=user_id, tag="Poupança"),
        models.Goal(name="Viagem", amount=5000.0, user_id=user_id, tag="Viagem")
    ]
    db.add_all(default_goals)
    db.commit()

@router.post("/revenues/", response_model=schemas.RevenueOut)
async def create_revenue(
    revenue: schemas.RevenueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_revenue = models.Revenue(name=revenue.name, amount=revenue.amount, user_id=current_user.id)
    db.add(db_revenue)
    db.commit()
    db.refresh(db_revenue)
    current_user.total_balance += revenue.amount
    db.commit()
    return db_revenue

@router.get("/revenues/", response_model=List[schemas.RevenueOut])
async def get_revenues(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    revenues = db.query(models.Revenue).filter(models.Revenue.user_id == current_user.id).all()
    return revenues

@router.delete("/revenues/{revenue_id}", response_model=schemas.Message)
async def delete_revenue(
    revenue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    revenue = db.query(models.Revenue).filter(
        models.Revenue.id == revenue_id,
        models.Revenue.user_id == current_user.id
    ).first()
    if not revenue:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    current_user.total_balance -= revenue.amount
    db.delete(revenue)
    db.commit()
    return {"message": "Receita deletada com sucesso"}

@router.post("/expenses/", response_model=schemas.ExpenseOut)
async def create_expense(
    expense: schemas.ExpenseCreateWithTag,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_expense = models.Expense(name=expense.name, amount=expense.amount, user_id=current_user.id, tag=expense.tag)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    current_user.total_balance -= expense.amount
    db.commit()
    return db_expense

@router.get("/expenses/", response_model=List[schemas.ExpenseOut])
async def get_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()
    return expenses

@router.delete("/expenses/{expense_id}", response_model=schemas.Message)
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    current_user.total_balance += expense.amount
    db.delete(expense)
    db.commit()
    return {"message": "Despesa deletada com sucesso"}

@router.post("/goals/", response_model=schemas.GoalOut)
async def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_goal = models.Goal(name=goal.name, amount=goal.amount, user_id=current_user.id, tag=goal.tag)  # Usando o tag do schema
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.get("/goals/", response_model=List[schemas.GoalOut])
async def get_goals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    return goals

@router.put("/goals/{goal_id}", response_model=schemas.GoalOut)
async def update_goal(
    goal_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db_goal.name = goal.name
    db_goal.amount = goal.amount
    db_goal.tag = goal.tag
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.delete("/goals/{goal_id}", response_model=schemas.Message)
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db.query(models.Expense).filter(models.Expense.tag == goal.tag, models.Expense.user_id == current_user.id).update({"tag": None})
    db.delete(goal)
    db.commit()
    return {"message": "Meta deletada com sucesso"}

@router.get("/balance/", response_model=float)
async def get_balance(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return current_user.total_balance

@router.put("/goals/{goal_id}", response_model=schemas.GoalOut)
def update_goal(
    goal_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == current_user.id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    db_goal.name = goal.name
    db_goal.amount = goal.amount
    db_goal.tag = goal.tag
    db.commit()
    db.refresh(db_goal)
    return db_goal