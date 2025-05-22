import uuid

import factory

from src.models.person import Person


class PersonFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("name")

    class Meta:
        model = Person
