import sys
import os
import asyncio

# Asegurar que el directorio raíz de la app esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base
# Importar todos los modelos para que Base.metadata los reconozca al crear las tablas
from app.db import models
from app.db.models import User
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fabricador de sesiones asíncronas para operaciones en la base de datos
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    print("Iniciando la creación de tablas en la base de datos...")
    async with engine.begin() as conn:
        # Crea todas las tablas definidas en los modelos si aún no existen
        await conn.run_sync(Base.metadata.create_all)
    print("¡Tablas creadas exitosamente!")

    print("Configurando usuario administrador por defecto...")
    async with AsyncSessionLocal() as db:
        # 1. Buscar si ya existe el usuario admin
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalars().first()

        # 2. Si existe, lo eliminamos para actualizar credenciales limpiamente
        if admin:
            print("Usuario admin existente encontrado. Recreando...")
            await db.delete(admin)
            await db.commit()

        # 3. Creamos el administrador inicial
        hashed_password = pwd_context.hash("admin123")
        new_admin = User(
            name="Admin",
            lastname="Regalito",
            code="ADM-001",
            username="admin",
            password_hash=hashed_password,
            role_id=1,          
            department_id=1,    
            is_active=True
        )
        db.add(new_admin)
        await db.commit()
        print("¡Usuario administrador configurado con éxito! (admin / admin123)")

if __name__ == "__main__":
    asyncio.run(init_db())