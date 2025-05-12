from datetime import datetime

from sqlalchemy import Column, String, Date, func  # type: ignore
from sqlalchemy.orm import (  # type: ignore
    Mapped,
    mapped_column,
    registry,
)

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    """
    primary_key: diz que o campo será a chave primária da tabela
    unique: diz que o campo só pode ter um valor único em toda a tabela.
    Não podemos ter um username repetido no banco, por exemplo.
    server_default: executa uma função no momento em que
    o objeto for instanciado.

    """

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
