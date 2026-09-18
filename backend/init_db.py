import sys
import os
import asyncio

# Forzamos a Python a reconocer la carpeta backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base
from app.db.models import User
from passlib.context import CryptContext
from sqlalchemy.future import select

# Importamos las herramientas asíncronas correctas de SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Creamos nuestro propio fabricador de sesiones asíncronas para este script
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    print("Conectando a la base de datos asíncrona y creando tablas...")
    
   # Usamos nuestro nuevo fabricador de sesiones asíncronas
    async with AsyncSessionLocal() as db:
        # 1. Buscar al usuario
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalars().first()

        # 2. Si existe, lo eliminamos
        if admin:
            print("Usuario encontrado. Eliminándolo para recrearlo...")
            await db.delete(admin)
            await db.commit()

        # 3. Lo creamos de nuevo desde cero
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
        print("¡Usuario administrador recreado con éxito! (admin / admin123)")

if __name__ == "__main__":
    asyncio.run(init_db())