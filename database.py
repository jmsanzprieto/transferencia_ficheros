from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# URL de la base de datos SQLite. Se creará un archivo './sql_app.db'
# Cargar las variables de entorno (es buena práctica cargarla donde se use, o al inicio en main.py)
from dotenv import load_dotenv
import os
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Crea un motor de SQLAlchemy. 'connect_args' es necesario para SQLite en algunos casos.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Base declarativa para los modelos de SQLAlchemy
Base = declarative_base()

# Configuración de la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definición del modelo de la tabla de usuarios
class User(Base):
    __tablename__ = "users"

    id_usuario = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hash_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# NUEVO MODELO: Definición del modelo de la tabla de archivos
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    uuid_name = Column(String, unique=True, index=True, nullable=False)
    original_filename = Column(String, nullable=False) # Para guardar el nombre original
    upload_date = Column(DateTime, default=datetime.now)
    downloaded = Column(Boolean, default=False) # Campo 'downloaded' con valor por defecto 0 (False)

# Función para crear todas las tablas definidas en Base
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)