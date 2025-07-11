import os
from datetime import datetime, timedelta
import jwt  # pyjwt
import uuid

# Load from env or set defaults
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "iat": now,
        "exp": expire,
        "type": "access",
        "sub": str(data.get("sub")),  # user identifier
        "jti": str(uuid.uuid4())  # unique token identifier
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(days=7)  # or use .env for flexibility
    to_encode.update({
        "iat": now,
        "exp": expire,
        "type": "refresh",
        "sub": str(data.get("sub")),
        "jti": str(uuid.uuid4())  # unique token identifier
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # Token expired
        raise
    except jwt.InvalidTokenError:
        # Invalid token (bad signature, malformed, etc.)
        raise
