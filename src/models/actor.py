import uuid

from pydantic import Field

from .person import Person


class Actor(Person):
    ...
