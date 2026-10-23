from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.repositories import HealthRepository

class HealthRepositoryImpl(HealthRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ping(self) -> bool:
        try:
            result = await self.db.execute(text("SELECT 1"))
            return result.scalar() == 1
        except Exception:
            return False
