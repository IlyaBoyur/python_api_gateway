import uuid

from src.models.base import BaseOutSchema
from src.models.writer import Writer


class WriterOutSchema(BaseOutSchema):
    id: uuid.UUID | str
    name: str

    @classmethod
    def from_entity(cls, writer: Writer) -> "WriterOutSchema":
        return WriterOutSchema(
            id=writer.id,
            name=writer.name,
        )
