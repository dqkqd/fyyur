from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import DeclarativeBase


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def to_orm(self, orm_class: type[DeclarativeBase]) -> DeclarativeBase:
        return orm_class(**self.model_dump())
