from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from back_app.database import get_session
from back_app.models import User
from back_app.settings import Settings

settings = Settings()

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        'exp': expire,
        'sub': data.get("sub")  # garante que sub esteja no token
    })
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(session: Session, email: str, password: str):
    user = session.scalar(select(User).where(User.email == email))
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get('sub')

        # print(f"DEBUG - Email do token: {username}")

        if username is None:
            raise credentials_exception

    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == username))

    # print(f"DEBUG - Usuário encontrado: id={user.id if user else 'None'}, email={user.email if user else 'None'}")

    if user is None:
        raise credentials_exception

    return user
