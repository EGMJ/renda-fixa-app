# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from app.models.auth import Token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

# Mock de banco de dados
fake_users_db = {
    "danielle": {
        "username": "danielle",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57THp.E1SlgO", # senha: '123'
        "disabled": False,
    }
}