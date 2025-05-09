from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    nickname = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    gender = Column(String)
    birth_date = Column(Date)
    is_active = Column(Boolean, default=True)
    profile_picture = Column(String)  