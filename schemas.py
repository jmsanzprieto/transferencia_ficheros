from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Esquemas de usuario
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id_usuario: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# Esquema para el login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Esquema para la respuesta del token JWT
class Token(BaseModel):
    access_token: str
    token_type: str

# Esquema para los datos dentro del token JWT (payload)
class TokenData(BaseModel):
    email: Optional[str] = None

# NUEVOS ESQUEMAS: Para archivos
class FileUploadResponse(BaseModel):
    filename: str
    uuid_name: str
    message: str
    upload_date: datetime
    downloaded: int
    download_url: str # <-- ¡ESTO SÍ DEBE EXISTIR EN EL ESQUEMA PYDANTIC!

    class Config:
        from_attributes = True # Permite mapeo de ORM (File, en este caso)
        # Esto es importante para que el esquema Pydantic pueda tomar datos de tu modelo SQLAlchemy File,
        # pero download_url se añadirá manualmente en el router.

class FileRecordBase(BaseModel):
    original_filename: str
    uuid_name: str

class FileRecordResponse(FileRecordBase):
    id: int
    upload_date: datetime
    downloaded: int # Representa el contador de descargas en la DB
    # user_id: int # Si asocias archivos a usuarios (esto iría en la DB)

    class Config:
        from_attributes = True