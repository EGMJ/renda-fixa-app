from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from app.models.auth import Token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

# Mock de banco
fake_users_db = {
    "danielle": {
        "username": "danielle",
        "hashed_password": "$2b$12$nWnjazbpIt1Hek021pRmu.lqA.YULLmG2QS8vkDwmMpRuxUAVaVXi",  # senha: 123
        "disabled": False,
    }
}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = create_access_token(
        data={"sub": user["username"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}