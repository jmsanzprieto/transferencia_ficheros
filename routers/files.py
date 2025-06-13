# routers/files.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse # Para servir archivos directamente
from starlette.background import BackgroundTask # ¡Importante!

from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid

import crud
import schemas
from dependencies import get_db
import security

from dotenv import load_dotenv

load_dotenv()
APP_URL = os.getenv("APP_URL")

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

# --- Configuración para la carga de archivos ---
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploaded_files")
ALLOWED_FILE_TYPES = [
    ftype.strip() for ftype in os.getenv("ALLOWED_FILE_TYPES", "application/pdf").split(',')
]

os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# --- Función de limpieza que se ejecutará en segundo plano ---
# Asegúrate de que esta función esté definida antes de que se use en download_file
def cleanup_file_and_record(file_path: str, uuid_name: str, db_session: Session):
    """
    Elimina el archivo físico del disco y su registro de la base de datos.
    Se ejecuta como una tarea en segundo plano después de que el archivo es servido.
    """
    try:
        # Borrar el archivo del disco
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Archivo {file_path} borrado del disco.")
        
        # Borrar el registro de la base de datos
        # Nota: La sesión 'db_session' se pasa aquí. Asegúrate de que sea segura de usar
        # en un contexto de segundo plano. En un entorno de producción con SQLAlchemy,
        # a menudo se crea una nueva sesión para tareas en segundo plano para evitar 
        # problemas de concurrencia o estado de la sesión principal.
        # Para este ejemplo, asumimos que pasar la sesión directamente es suficiente,
        # pero si ves errores de sesión más adelante, considera obtener una nueva sesión
        # dentro de esta función, por ejemplo:
        # with get_db() as session:
        #    crud.delete_file_record(session, uuid_name=uuid_name)
        
        crud.delete_file_record(db_session, uuid_name=uuid_name)
        print(f"Registro del archivo {uuid_name} borrado de la base de datos.")

    except Exception as e:
        # Aquí puedes loggear el error o manejarlo de alguna otra forma.
        # No queremos que una falla en la limpieza rompa la descarga principal.
        print(f"Error en la tarea de limpieza para {uuid_name}: {e}")

# --- Endpoint para cargar un archivo (PROTEGIDO) ---
@router.post("/upload", response_model=schemas.FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(security.get_current_user)
):
    print(f"Usuario {current_user.email} está subiendo un archivo.")

    # 1. Validación de tamaño
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo es demasiado grande. Tamaño máximo permitido: {MAX_FILE_SIZE_MB}MB."
        )

    # 2. Validación de tipo de archivo (MIME type)
    print(f"DEBUG: Tipo de contenido recibido: {file.content_type}")
    print(f"DEBUG: Tipos permitidos: {ALLOWED_FILE_TYPES}")

    if file.content_type not in ALLOWED_FILE_TYPES:
        if file.filename and file.filename.lower().endswith('.pdf'):
            print("DEBUG: Tipo MIME recibido incorrecto, pero la extensión es .pdf. Aceptando.")
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Tipo de archivo no permitido. Solo se permiten: {', '.join(ALLOWED_FILE_TYPES)}"
            )

    # 3. Generar un nombre único con UUID y guardar el archivo
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el archivo: {e}"
        )

    # 4. Registrar el archivo en la base de datos
    file_record = crud.create_file_record(
        db=db,
        original_filename=file.filename,
        uuid_name=unique_filename,
    )

    # 5. Devolver la respuesta exitosa incluyendo la URL de descarga
    download_url = f"{APP_URL}files/download/{unique_filename}"

    return schemas.FileUploadResponse(
        filename=file.filename,
        uuid_name=unique_filename,
        message="Archivo cargado exitosamente",
        upload_date=file_record.upload_date,
        downloaded=file_record.downloaded,
        download_url=download_url
    )
# --- Endpoint para descargar un archivo por UUID (SIN PROTECCIÓN) ---
@router.get("/download/{uuid_name}")
async def download_file(
    uuid_name: str,
    db: Session = Depends(get_db)
):
    # 1. Obtener el registro del archivo de la base de datos
    file_record = crud.get_file_record_by_uuid(db, uuid_name=uuid_name)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado.")

    file_path = os.path.join(UPLOAD_DIRECTORY, file_record.uuid_name) 
    
    # 2. Comprobar si el archivo existe en el disco
    if not os.path.exists(file_path):
        crud.delete_file_record(db, uuid_name=uuid_name)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado en el servidor.")

    # 3. Incrementar contador de descarga
    crud.increment_file_download_count(db, uuid_name=uuid_name)

    # 4. Servir el archivo para descarga y programar el borrado como tarea en segundo plano
    try:
        response = FileResponse(
            path=file_path,
            filename=file_record.original_filename,
            media_type="application/octet-stream",
            # Aquí es donde adjuntamos la tarea de limpieza
            background=BackgroundTask(cleanup_file_and_record, file_path, uuid_name, db)
        )
        return response
    except Exception as e:
        print(f"Error al preparar la descarga del archivo {file_record.uuid_name}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al procesar la descarga del archivo.")

# --- Endpoint para ver todos los registros de archivos cargados (PROTEGIDO) ---
@router.get("/records", response_model=List[schemas.FileRecordResponse])
async def get_all_file_records(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(security.get_current_user)
):
    file_records = crud.get_all_file_records(db)
    return file_records