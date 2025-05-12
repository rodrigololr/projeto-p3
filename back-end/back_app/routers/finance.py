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
    db.delete(revenue)
    db.commit()
    return {"message": "Receita deletada com sucesso"}

@router.post("/expenses/", response_model=schemas.ExpenseOut)
async def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_expense = models.Expense(name=expense.name, amount=expense.amount, user_id=current_user.id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
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
    db.delete(expense)
    db.commit()
    return {"message": "Despesa deletada com sucesso"}