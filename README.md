# API de Carga y Descarga de Archivos (Estilo WeTransfer)

## Descripción del Proyecto
Esta API FastAPI permite la **carga y descarga segura de archivos**, con un enfoque en la **autenticación** de usuarios, similar a la funcionalidad que ofrece un servicio como WeTransfer. Su objetivo es proporcionar una solución robusta y escalable para la gestión de archivos, asegurando que solo los usuarios autorizados puedan interactuar con ellos.

---

## Características Principales
* **Carga de archivos**: Soporta la subida de archivos .
* **Descarga de archivos**: Permite la recuperación de archivos específicos por su UUID.
* **Autenticación de usuarios**: Implementa un sistema de autenticación basado en tokens (OAuth2/JWT) para proteger los endpoints.
* **Estructura modular**: Diseñado para ser extensible y fácil de mantener.

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
    (Reemplaza `tu_usuario/tu_proyecto` con la URL real de tu repositorio)

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
    pip install "fastapi[all]" uvicorn python-multipart
    # Si usas JWT para la autenticación, también necesitarás:
    # pip install python-jose[cryptography] passlib[bcrypt]
    ```

4.  **Configura las variables de entorno** (si las usas para secretos como `SECRET_KEY` o credenciales de base de datos). Puedes crear un archivo `.env` en la raíz del proyecto y cargarlo con `python-dotenv`.

---

## Uso de la API

### 1. Iniciar la aplicación

Ejecuta la API usando Uvicorn:

```bash
uvicorn main:app --reload