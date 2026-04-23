import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import models
from database import Base
from main import app, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_cookbook.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

models.Base.metadata.bind = engine


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_recipe(client: AsyncClient):
    response = await client.post(
        "/recipes",
        json={
            "name": "Тестовый салат",
            "cooking_time": 15,
            "ingredients": "Помидоры, Огурцы",
            "description": "Порезать и смешать",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Тестовый салат"
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_get_recipes_list(client: AsyncClient):
    await client.post(
        "/recipes",
        json={"name": "А", "cooking_time": 10, "ingredients": "a", "description": "a"},
    )
    await client.post(
        "/recipes",
        json={"name": "Б", "cooking_time": 20, "ingredients": "b", "description": "b"},
    )

    response = await client.get("/recipes")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_recipe_detail_and_views(client: AsyncClient):
    create_resp = await client.post(
        "/recipes",
        json={
            "name": "Суп",
            "cooking_time": 30,
            "ingredients": "Вода",
            "description": "Вскипятить",
        },
    )
    recipe_id = create_resp.json()["id"]

    resp1 = await client.get(f"/recipes/{recipe_id}")
    assert resp1.status_code == 200
    assert resp1.json()["views"] == 1

    resp2 = await client.get(f"/recipes/{recipe_id}")
    assert resp2.json()["views"] == 2


@pytest.mark.asyncio
async def test_get_nonexistent_recipe(client: AsyncClient):
    response = await client.get("/recipes/999")
    assert response.status_code == 404
