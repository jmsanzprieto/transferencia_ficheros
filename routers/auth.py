from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importar desde tus nuevos archivos de lógica
import crud
import schemas
import security
from dependencies import get_db

# Crear un router de FastAPI
router = APIRouter(
    prefix="/auth", # Todas las rutas en este archivo empezarán con /auth
    tags=["Auth"], # Etiqueta para la documentación de Swagger UI
)

# Endpoint para registrar un nuevo usuario
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )
    
    hashed_password = security.get_password_hash(user.password)
    new_user = crud.create_user(db=db, user=user, hashed_password=hashed_password)
    
    return new_user

# Endpoint para el login y obtención del token JWT
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    user_login: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db, email=user_login.email)
    
    if not db_user or not security.authenticate_user(user_login.password, db_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = security.timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para obtener todos los usuarios (para depuración, sin hash)
@router.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return users