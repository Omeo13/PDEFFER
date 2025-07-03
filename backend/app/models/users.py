from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# SQLAlchemy User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    last_logon = Column(String, nullable=True)

# Pydantic models for request and response
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str  # Plain password input

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: str
    last_logon: str | None = None

    class Config:
        from_attributes = True
