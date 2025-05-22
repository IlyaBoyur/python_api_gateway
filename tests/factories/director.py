import uuid

import factory

from src.models.director import Director


class DirectorFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("name")

    class Meta:
        model = Director
