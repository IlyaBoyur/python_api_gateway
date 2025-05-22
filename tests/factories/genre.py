import uuid

import factory

from src.models.genre import Genre


class GenreFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("name")
    description = factory.Faker("text")
    
    class Meta:
        model = Genre
