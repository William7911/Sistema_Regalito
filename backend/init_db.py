import asyncio
import os
import sys

# Asegurar que el directorio raíz de la app esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base
# Importar todos los modelos para que Base.metadata los reconozca
from app.db import models

async def init_db():
    print("Iniciando la creación de tablas en la base de datos...")
    async with engine.begin() as conn:
        # Crea todas las tablas definidas en los modelos
        await conn.run_sync(Base.metadata.create_all)
    print("¡Tablas creadas exitosamente!")

if __name__ == "__main__":
    asyncio.run(init_db())
