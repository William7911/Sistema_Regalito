from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api import auth, cash_register, categories, departments, products, roles, users
from app.db.database import engine, Base
import logging
import os

# Opcional: Crear tablas automáticamente para desarrollo. En prod usar Alembic
# Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tienda el Regalito POS API")

# Configurar CORS (seguridad web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se debería especificar el origen (ej. http://localhost:8000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Manejo de errores global (los controladores no usan try/except)
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(cash_register.router, prefix="/api/caja", tags=["caja"])
app.include_router(categories.router, prefix="/api/categorias", tags=["categorias"])
app.include_router(products.router, prefix="/api/productos", tags=["productos"])
app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
app.include_router(departments.router, prefix="/api/departamentos", tags=["departamentos"])
app.include_router(users.router, prefix="/api/usuarios", tags=["usuarios"])

# Servir archivos estáticos del frontend en la ruta principal (Recomendado para simplicidad)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")