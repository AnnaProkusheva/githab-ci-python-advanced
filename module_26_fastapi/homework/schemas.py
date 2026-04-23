from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    name: str = Field(..., description="Название блюда", examples=["Оливье"])
    cooking_time: int = Field(
        ..., description="Время приготовления в минутах", examples=[30]
    )
    ingredients: str = Field(
        ...,
        description="Список ингредиентов через запятую",
        examples=["Яйца, Майонез, Картофель"],
    )
    description: str = Field(
        ...,
        description="Описание процесса приготовления",
        examples=["Сварить овощи..."],
    )


class RecipeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    views: int
    cooking_time: int


class RecipeDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cooking_time: int
    ingredients: str
    description: str
    views: int
