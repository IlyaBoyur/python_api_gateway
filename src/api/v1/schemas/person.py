import uuid

from pydantic import BaseModel, Field

from src.models.base import BaseOutSchema
from src.models.person import Person


class PersonOutSchema(BaseOutSchema):
    id: uuid.UUID | str = Field(description="ID")
    name: str = Field(description="Имя")

    @classmethod
    def from_entity(cls, person: Person) -> "PersonOutSchema":
        return PersonOutSchema(
            id=person.id,
            name=person.name,
        )


class PersonMultiOutSchema(BaseModel):
    results: list[PersonOutSchema]
