import uuid

import factory

from src.models.actor import Actor


class ActorFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("name")

    class Meta:
        model = Actor
