import uuid

import factory

from src.models.writer import Writer


class WriterFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("name")

    class Meta:
        model = Writer
