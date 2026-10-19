import pytest
from app.main import app
from app.db.database import get_db

@pytest.fixture
async def client(db_session):
    from httpx import AsyncClient, ASGITransport
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health_check_endpoint(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"
    assert data["api"] == "ok"
