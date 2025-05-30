from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Column, Date, ForeignKey, String, Float, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()

@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    total_balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

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
    identificador: Mapped[str] = mapped_column(
        default_factory=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

@table_registry.mapped_as_dataclass
class Expense:
    __tablename__ = 'expenses'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    identificador: Mapped[str] = mapped_column(
        default_factory=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

@table_registry.mapped_as_dataclass
class Goal:
    __tablename__ = 'goals'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    amount: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tag: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
