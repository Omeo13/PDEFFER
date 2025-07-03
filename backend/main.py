from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import engine, SessionLocal
from app.models.users import Base, User, UserCreate, UserRead

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.users import User, UserCreate, UserRead, Base
from app.utils.database import SessionLocal, engine
from datetime import datetime
from passlib.context import CryptContext

app = FastAPI()
Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.name == user.name) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        created_at=datetime.utcnow().isoformat(),
        last_logon=None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
