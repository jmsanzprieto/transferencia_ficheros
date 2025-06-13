from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles # Para servir archivos estáticos (si los tuvieras)
from fastapi.templating import Jinja2Templates # Para Jinja2

from database import create_db_and_tables
from routers import auth
from routers import files

app = FastAPI(
    title="API de Carga y Descarga de Archivos",
    description="Una API robusta para cargar y descargar archivos de forma segura, similar a la funcionalidad de WeTransfer, con autenticación de usuarios.",
    version="1.0.0",
    contact={
        "name": "José Manuel Sanz",
        "email": "contacto@josemanuelsanz.es"
    }
)
# Configuración de Jinja2Templates: especifica la carpeta donde están tus plantillas HTML
templates = Jinja2Templates(directory="templates")

# Opcional: Si tuvieras archivos CSS/JS locales en una carpeta 'static'
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Evento de inicio de la aplicación para crear las tablas
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("Base de datos y tablas creadas (si no existían).")

# Incluye las rutas de la API (login, carga de archivos, etc.)
app.include_router(auth.router)
app.include_router(files.router)

# --- Nueva ruta para servir la página de login ---
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Sirve la página principal que contiene el formulario de login.
    """
    return templates.TemplateResponse("login.html", {"request": request})

# Endpoint de prueba para la API (no la página HTML)
@app.get("/api-status")
def api_status():
    return {"message": "¡API de usuarios, autenticación y archivos funcionando!"}