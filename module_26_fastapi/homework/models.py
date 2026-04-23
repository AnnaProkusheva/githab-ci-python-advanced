from sqlalchemy import Column, Integer, String, Text

from database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cooking_time = Column(Integer, nullable=False)
    ingredients = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    views = Column(Integer, default=0)  # type: ignore[assignment]
