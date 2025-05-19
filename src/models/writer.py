import uuid

from pydantic import Field

from .person import Person


class Writer(Person):
    ...
