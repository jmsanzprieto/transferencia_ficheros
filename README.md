# API de Carga y Descarga de Archivos (Estilo WeTransfer)

## Descripción del Proyecto
Esta API FastAPI permite la **carga y descarga segura de archivos**, con un enfoque en la **autenticación** de usuarios, similar a la funcionalidad que ofrece un servicio como WeTransfer. Su objetivo es proporcionar una solución robusta y escalable para la gestión de archivos, asegurando que solo los usuarios autorizados puedan interactuar con ellos.

---

## Características Principales
* **Autenticación de usuarios**: Implementa un sistema de autenticación basado en tokens JWT (JSON Web Tokens) usando OAuth2 para proteger los endpoints.
* **Registro de usuarios**: Permite a nuevos usuarios registrarse con email y contraseña.
* **Gestión de contraseñas segura**: Las contraseñas de los usuarios se almacenan de forma segura utilizando el algoritmo de hashing Argon2.
* **Carga de archivos**: Permite la subida de archivos, con validaciones de tamaño y tipo de archivo.
* **Descarga de archivos**: Permite la recuperación de archivos específicos por un UUID único. Los archivos se sirven y, opcionalmente, se limpian del servidor después de la descarga.
* **Persistencia de datos**: Utiliza SQLite como base de datos para almacenar registros de usuarios y archivos, gestionada a través de SQLAlchemy.
* **Documentación automática**: Genera automáticamente interfaces de documentación interactiva (Swagger UI y Redoc).
* **Frontend básico**: Incluye una página de inicio de sesión simple con Jinja2.

---

## Requisitos del Sistema
Asegúrate de tener instalado lo siguiente:
* **Python 3.8 o superior**
* **pip** (el gestor de paquetes de Python)

---

## Instalación y Configuración

Sigue estos pasos para poner la API en marcha en tu entorno local:

1.  **Clona el repositorio** (si aún no lo has hecho):
    ```bash
    git clone [https://github.com/tu_usuario/tu_proyecto.git](https://github.com/tu_usuario/tu_proyecto.git)
    cd tu_proyecto
    ```
    *(Reemplaza `tu_usuario/tu_proyecto` con la URL real de tu repositorio)*

2.  **Crea y activa un entorno virtual** (recomendado para aislar las dependencias):
    ```bash
    python -m venv venv
    # En Linux/macOS:
    source venv/bin/activate
    # En Windows:
    .\venv\Scripts\activate
    ```

3.  **Instala las dependencias** del proyecto:
    ```bash
    pip install -r requirements.txt
    ```
    (El archivo `requirements.txt` se generará por separado con todas las dependencias necesarias).

4.  **Configura las variables de entorno**:
    Crea un archivo `.env` en la raíz de tu proyecto con el siguiente contenido:
    ```
    SECRET_KEY="tu_super_secreto_para_jwt_cambialo"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    DATABASE_URL="sqlite:///./sql_app.db"
    APP_URL="http://localhost:8000/" # Asegúrate que coincida con la URL de tu app
    MAX_FILE_SIZE_MB=10 # Tamaño máximo de archivo permitido en MB
    ALLOWED_FILE_TYPES="application/pdf,image/jpeg,image/png,text/plain" # Tipos MIME permitidos (separados por comas)
    UPLOAD_DIRECTORY="uploaded_files" # Directorio donde se guardarán los archivos subidos
    ```
    **¡Importante!** Cambia `tu_super_secreto_para_jwt_cambialo` por una cadena larga y segura.

5.  **Crea el directorio de subidas**:
    Asegúrate de que el directorio especificado en `UPLOAD_DIRECTORY` (por defecto `uploaded_files`) exista en la raíz de tu proyecto. Puedes crearlo manualmente o se creará automáticamente cuando la aplicación intente guardar el primer archivo.

---

## Uso de la API

### 1. Iniciar la aplicación

Ejecuta la API usando Uvicorn desde la raíz de tu proyecto:

```bash
uvicorn main:app --reload
