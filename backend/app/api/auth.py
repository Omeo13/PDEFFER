import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from app.utils.jwt_helpers import create_access_token, create_refresh_token, decode_token
from jose import JWTError
from datetime import timedelta
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

# Temporary in-memory user store (replace with real user management later)
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": pwd_context.hash("secret123"),
        "id": "1"
    }
}

refresh_token_expires_delta = timedelta(days=7)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": user["id"]})
    refresh_token_str = create_refresh_token({"sub": user["id"]})

    # No DB storage or revocation for refresh tokens

    return JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer"
    })

@router.post("/refresh")
def refresh_token(request: Request, response: Response):
    cookie_token = request.cookies.get("refresh_token")
    if not cookie_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_token(cookie_token)
        token_sub = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # No DB check for revocation or expiration - assume valid token

    new_access_token = create_access_token({"sub": token_sub})
    new_refresh_token = create_refresh_token({"sub": token_sub})

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/refresh",
        max_age=refresh_token_expires_delta.total_seconds()
    )

    return {"access_token": new_access_token, "token_type": "bearer"}
