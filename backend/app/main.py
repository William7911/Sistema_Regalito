from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api import auth, cash_register, catalogos, catalogos_generales, categories, compras, dashboard, departments, mermas, products, roles, sales, users, sync, health, reportes, configuracion, inventory, facturacion, clientes, tipos_cliente, bitacora, historial_precios, traslados, visitas
from app.db.database import engine, Base
import logging
import os

# Opcional: Crear tablas automáticamente para desarrollo. En prod usar Alembic
# Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager
from app.core.sync_daemon import sync_daemon

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: iniciar el daemon de sincronizacion
    await sync_daemon.start()
    yield
    # Shutdown: detener el daemon limpiamente
    await sync_daemon.stop()

from app.core.config import settings

app = FastAPI(
    title="Tienda el Regalito POS API", 
    lifespan=lifespan,
    debug=(settings.ENVIRONMENT != "production"),
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

# Configurar CORS (seguridad web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
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
app.include_router(sales.router, prefix="/api/ventas", tags=["ventas"])
app.include_router(facturacion.router, prefix="/api/facturacion", tags=["facturacion"])
app.include_router(mermas.router, prefix="/api/mermas", tags=["mermas"])
app.include_router(categories.router, prefix="/api/categorias", tags=["categorias"])
app.include_router(products.router, prefix="/api/productos", tags=["productos"])
app.include_router(catalogos.router, prefix="/api/catalogos", tags=["catalogos"])
app.include_router(catalogos_generales.router, prefix="/api/catalogos", tags=["catalogos"])
app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
app.include_router(departments.router, prefix="/api/departamentos", tags=["departamentos"])
app.include_router(users.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["clientes"])
app.include_router(tipos_cliente.router, prefix="/api/tipos-cliente", tags=["tipos-cliente"])
app.include_router(compras.router, prefix="/api/compras", tags=["compras"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(reportes.router)
app.include_router(configuracion.router)
app.include_router(inventory.router)
app.include_router(inventory.inventario_router)
app.include_router(dashboard.router)
app.include_router(bitacora.router, prefix="/api/bitacora", tags=["bitacora"])
app.include_router(historial_precios.router, prefix="/api/historial-precios", tags=["historial-precios"])
app.include_router(traslados.router, prefix="/api/traslados", tags=["traslados"])
app.include_router(visitas.router, prefix="/api/visitas", tags=["visitas"])

# Servir imágenes subidas por los usuarios
uploads_path = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_path, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=uploads_path), name="uploads")

# Servir archivos estáticos del frontend en la ruta principal (Recomendado para simplicidad)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")