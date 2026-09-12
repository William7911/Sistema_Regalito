from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, cash_register, products
from app.db.database import engine, Base
import os

# Opcional: Crear tablas automáticamente para desarrollo. En prod usar Alembic
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tienda el Regalito POS API")

# Configurar CORS (seguridad web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se debería especificar el origen (ej. http://localhost:8000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(cash_register.router, prefix="/api/caja", tags=["caja"])
app.include_router(products.router, prefix="/api/productos", tags=["productos"])

# Servir archivos estáticos del frontend en la ruta principal (Recomendado para simplicidad)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
