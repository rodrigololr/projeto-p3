from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr  # type: ignore


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    gender: Optional[str]
    birth_date: Optional[date]

    class Config:
        from_attributes = True


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserOut(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    total_balance: float
    model_config = ConfigDict(from_attributes=True)


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class RevenueBase(BaseModel):
    name: str
    amount: float


class RevenueCreate(RevenueBase):
    pass


class RevenueOut(RevenueBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExpenseBase(BaseModel):
    name: str
    amount: float


class ExpenseCreateWithTag(ExpenseBase):
    tag: Optional[str] = None


class ExpenseOut(ExpenseBase):
    id: int
    user_id: int
    tag: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GoalBase(BaseModel):
    name: str
    amount: float


class GoalCreate(GoalBase):
    tag: str  # Adicionando tag como campo opcional


class GoalOut(GoalBase):
    id: int
    user_id: int
    tag: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GoalList(BaseModel):
    goals: List[GoalOut]


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    username: Optional[str] = None
