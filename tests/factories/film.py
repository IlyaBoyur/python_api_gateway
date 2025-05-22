import uuid

import factory
from faker import Faker

from src.models.film import Film
from tests.factories.actor import ActorFactory
from tests.factories.director import DirectorFactory
from tests.factories.writer import WriterFactory

fake = Faker()


class FilmFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    title = factory.Faker("word")
    description = factory.Faker("text")
    imdb_rating = factory.Faker("pyfloat", min_value=5.0, max_value=9.9)
    genres = factory.Faker("word")
    actors_names = factory.Faker("word")
    directors_names = factory.Faker("word")
    writers_names = factory.Faker("word")

    actors = factory.LazyAttribute(
        lambda o: ActorFactory.build_batch(fake.random_int(min=5, max=10))
    )
    directors = factory.LazyAttribute(
        lambda o: DirectorFactory.build_batch(fake.random_int(min=1, max=2))
    )
    writers = factory.LazyAttribute(
        lambda o: WriterFactory.build_batch(fake.random_int(min=2, max=4))
    )

    class Meta:
        model = Film
