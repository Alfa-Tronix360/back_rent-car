from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas
from auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou palavra-passe incorretos.")
    if not user.ativo:
        raise HTTPException(status_code=403, detail="Conta desativada.")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "usuario": user}


@router.get("/profile", response_model=schemas.UsuarioOut)
def profile(user: models.Usuario = Depends(get_current_user)):
    return user
