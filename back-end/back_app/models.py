from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    String,
    Float,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    registry,
)

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    total_balance: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False)  # Valor padrão explícito

    full_name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)


@table_registry.mapped_as_dataclass
class Revenue:
    __tablename__ = 'revenues'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@table_registry.mapped_as_dataclass
class Expense:
    __tablename__ = 'expenses'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@table_registry.mapped_as_dataclass
class Goal:
    __tablename__ = 'goals'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tag: Mapped[str]
    type: Mapped[str] = mapped_column(String(50), default='despesa')
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


# ... (seu código existente para User, Revenue, Expense, Goal) ...

@table_registry.mapped_as_dataclass
class Account:
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(init=False, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(String(100), index=True)
    account_type: Mapped[str] = mapped_column(String(50))
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

@table_registry.mapped_as_dataclass
class CreditCard:
    __tablename__ = "credit_cards"

    id: Mapped[int] = mapped_column(init=False, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    name: Mapped[str] = mapped_column(String(100), index=True)  # Ex: "Cartão Nubank Gold"
    limit: Mapped[float] = mapped_column(Float)                 # Limite do cartão
    invoice_due_date_str: Mapped[str] = mapped_column(String(5)) # Para armazenar "DD/MM"
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Ex: "bi-credit-card"
    
    # Campos opcionais para considerar no futuro (para o resumo na principal.html):
    # current_spending: Mapped[float] = mapped_column(Float, default=0.0, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
