from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api import auth

app = FastAPI()

# Remove the startup event that creates tables since no DB is present

app.include_router(auth.router)
