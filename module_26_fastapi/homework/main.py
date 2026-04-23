from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from database import engine, get_db



@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(title="Cookbook API", lifespan=lifespan)

@app.post("/recipes", response_model=schemas.RecipeDetail, status_code=201)
async def create_recipe(recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    new_recipe = models.Recipe(**recipe.model_dump())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe


@app.get("/recipes", response_model=List[schemas.RecipeListItem])
async def get_recipes_list(db: AsyncSession = Depends(get_db)):
    stmt = select(models.Recipe).order_by(
        models.Recipe.views.desc(),
        models.Recipe.cooking_time.asc()
    )
    result = await db.execute(stmt)
    recipes = result.scalars().all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
async def get_recipe_detail(recipe_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Recipe).where(models.Recipe.id == recipe_id)
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)

    return recipe


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)