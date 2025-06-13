from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError # Importa PyJWTError para manejar errores de decodificación
from typing import Optional

# Importaciones para FastAPI Security y OAuth2
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from dotenv import load_dotenv
import os

from database import User # Necesitamos el modelo User para buscar el usuario en la DB
import crud # Necesitamos crud para obtener el usuario de la DB

# Cargar las variables de entorno del archivo .env
load_dotenv()

# --- Configuración de JWT ---
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada en el archivo .env o como variable de entorno.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Contexto para el hashing de contraseñas (usando Argon2)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Instancia de OAuth2BearerToken para la seguridad con "Bearer" token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Funciones de seguridad y JWT ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(password: str, db_user: User) -> bool:
    if not db_user:
        return False
    return verify_password(password, db_user.hash_password)

# NUEVA FUNCIÓN: Para decodificar y verificar el token JWT
def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        # Si la decodificación falla (token inválido, expirado, etc.)
        return None

# NUEVA DEPENDENCIA: Para obtener el usuario actual a partir del token JWT
# Necesitamos la sesión de DB aquí para buscar el usuario
from dependencies import get_db # Importa get_db desde dependencies
from schemas import TokenData # Importa TokenData para el tipo del payload

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # El "sub" (subject) del token contiene el email del usuario
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Crea un objeto TokenData para validar el email
    token_data = TokenData(email=email)
    
    # Busca el usuario en la base de datos
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user