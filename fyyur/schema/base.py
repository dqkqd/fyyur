from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


class BaseSchema(BaseModel):
    def to_orm(self, orm_class: type[DeclarativeBase]) -> DeclarativeBase:
        return orm_class(**self.model_dump())
