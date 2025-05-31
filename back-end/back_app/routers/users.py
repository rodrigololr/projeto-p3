# Users.py
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from sqlalchemy import select  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from datetime import datetime

from back_app.database import get_session
from back_app.models import User
from back_app.schemas import (
    Message,
    Token,
    UserOut,
    UserPublic,
    UserSchema,
    UserOut,
    UserUpdate

)
from back_app.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):  # type: ignore
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username, password=hashed_password, email=user.email
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.post('/login', response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: T_Session,  # type: ignore
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Email ou senha inválidos',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # cria token JWT com o e-mail como subject (sub)
    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me', response_model=UserOut)
def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user(
    user: UserUpdate,
    session: T_Session,  # type: ignore
    current_user: T_CurrentUser,
):
    try:
        if user.birth_date and isinstance(user.birth_date, str):
            user.birth_date = datetime.strptime(
                user.birth_date, "%Y-%m-%d").date()

        for field, value in user.dict(exclude_unset=True).items():
            setattr(current_user, field, value)

        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username already exists",
        )


@router.delete('/me', response_model=Message)
def delete_current_user(
    session: T_Session,
    current_user: T_CurrentUser,
):
    """
    Deleta a conta do usuário atual e todos os dados associados
    (revenues, expenses, goals).
    """
    try:
        # O SQLAlchemy com cascade="all, delete-orphan" vai automaticamente
        # deletar todos os registros relacionados
        session.delete(current_user)
        session.commit()
        
        return {'message': 'Account successfully deleted'}
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Error deleting account: {str(e)}'
        )


