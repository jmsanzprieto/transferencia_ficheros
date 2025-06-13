# crud.py

from sqlalchemy.orm import Session
from database import User, File # Importa los modelos
import schemas
from datetime import datetime # Para timestamp en el crud de archivos

# --- Operaciones CRUD de Usuario ---
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = User(email=user.email, hash_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Operaciones CRUD de Archivo ---
def create_file_record(db: Session, original_filename: str, uuid_name: str):
    """
    Crea un nuevo registro de archivo en la base de datos.
    """
    db_file = File(original_filename=original_filename, uuid_name=uuid_name, downloaded=0, upload_date=datetime.utcnow())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file_record_by_uuid(db: Session, uuid_name: str):
    """Recupera un registro de archivo por su UUID."""
    return db.query(File).filter(File.uuid_name == uuid_name).first()

def get_all_file_records(db: Session):
    """Recupera todos los registros de archivos."""
    return db.query(File).all()

def increment_file_download_count(db: Session, uuid_name: str):
    """Incrementa el contador de descargas para un registro de archivo."""
    db_file = db.query(File).filter(File.uuid_name == uuid_name).first()
    if db_file:
        db_file.downloaded += 1
        db.commit()
        db.refresh(db_file)
    return db_file

def delete_file_record(db: Session, uuid_name: str):
    """Elimina un registro de archivo de la base de datos."""
    db_file = db.query(File).filter(File.uuid_name == uuid_name).first()
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False