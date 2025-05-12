import uuid

from src.models.base import BaseOutSchema
from src.models.director import Director


class DirectorOutSchema(BaseOutSchema):
    id: uuid.UUID | str
    name: str

    @classmethod
    def from_entity(cls, director: Director) -> "DirectorOutSchema":
        return DirectorOutSchema(
            id=director.id,
            name=director.name,
        )
