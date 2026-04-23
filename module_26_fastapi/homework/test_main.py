import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from main import app, get_db
import models
import schemas


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_cookbook.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

models.Base.metadata.bind = engine


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)



@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Создаем транспорт, который подключается к FastAPI приложению
    transport = ASGITransport(app=app)

    # Передаем транспорт в клиент, а не app напрямую
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# --- ТЕСТЫ ---

@pytest.mark.asyncio
async def test_create_recipe(client: AsyncClient):
    """Тест создания рецепта (POST)"""
    response = await client.post(
        "/recipes",
        json={
            "name": "Тестовый салат",
            "cooking_time": 15,
            "ingredients": "Помидоры, Огурцы",
            "description": "Порезать и смешать"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Тестовый салат"
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_get_recipes_list(client: AsyncClient):
    """Тест получения списка рецептов (GET)"""
    # Сначала создадим два рецепта
    await client.post("/recipes", json={"name": "А", "cooking_time": 10, "ingredients": "a", "description": "a"})
    await client.post("/recipes", json={"name": "Б", "cooking_time": 20, "ingredients": "b", "description": "b"})

    # Получаем список
    response = await client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_recipe_detail_and_views(client: AsyncClient):
    """Тест детального просмотра и счетчика просмотров"""
    # Создаем рецепт
    create_resp = await client.post("/recipes", json={
        "name": "Суп",
        "cooking_time": 30,
        "ingredients": "Вода",
        "description": "Вскипятить"
    })
    recipe_id = create_resp.json()["id"]

    # Первый запрос детальной страницы
    resp1 = await client.get(f"/recipes/{recipe_id}")
    assert resp1.status_code == 200
    assert resp1.json()["views"] == 1

    # Второй запрос
    resp2 = await client.get(f"/recipes/{recipe_id}")
    assert resp2.json()["views"] == 2


@pytest.mark.asyncio
async def test_get_nonexistent_recipe(client: AsyncClient):
    """Тест поиска несуществующего рецепта (404)"""
    response = await client.get("/recipes/999")
    assert response.status_code == 404