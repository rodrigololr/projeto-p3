from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    full_name: str
    nickname: str
    gender: str
    birth_date: date
    profile_picture: str = None 

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str = None

class UserInDB(UserBase):
    id: int

    class Config:
        orm_mode = True
