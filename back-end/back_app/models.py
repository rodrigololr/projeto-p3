from datetime import datetime

from sqlalchemy import (  # type: ignore
    Column,
    Date,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import (  # type: ignore
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
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
