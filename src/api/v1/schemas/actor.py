import uuid

from src.models.actor import Actor
from src.models.base import BaseOutSchema


class ActorOutSchema(BaseOutSchema):
    id: uuid.UUID | str
    name: str

    @classmethod
    def from_entity(cls, actor: Actor) -> "ActorOutSchema":
        return ActorOutSchema(
            id=actor.id,
            name=actor.name,
        )
