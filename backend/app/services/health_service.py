from app.interfaces.services import HealthService
from app.interfaces.repositories import HealthRepository

class ConcreteHealthService(HealthService):
    def __init__(self, repo: HealthRepository):
        self.repo = repo

    async def check_health(self) -> dict:
        is_db_up = await self.repo.ping()
        return {
            "api": "ok",
            "db": "ok" if is_db_up else "error",
            "status": "ok" if is_db_up else "error"
        }
