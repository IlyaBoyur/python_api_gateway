import abc
import copy
from collections import OrderedDict
from types import MappingProxyType
from typing import Any

from .filter_fields import BaseFilter, Filter, OrderingField, OrderingFilter


class FilterSetMeta(abc.ABCMeta):
    def __new__(mcs, name: str, bases: tuple, attrs: dict[str, Any]) -> "FilterSetMeta":
        attrs["_declared_filters"] = mcs.get_declared_filters(bases, attrs)
        new_class = super().__new__(mcs, name, bases, attrs)
        return new_class

    @classmethod
    def get_declared_filters(mcs, _: tuple, attrs: dict[str, Any]) -> dict[str, BaseFilter]:
        filters: dict[str, BaseFilter] = OrderedDict()

        for filter_name, filter_ in list(attrs.items()):
            if not isinstance(filter_, BaseFilter):
                continue
            del attrs[filter_name]
            filters[filter_name] = filter_
            if getattr(filter_, "field_name", None) is None:
                filter_.field_name = filter_name

        return filters


class BaseFilterSet(metaclass=FilterSetMeta):
    _declared_filters: dict[str, BaseFilter]

    def __init__(
        self,
        query: dict[str, Any] | None = None,
    ):
        self.__base_query = query or {}
        self.filters = self.get_filters()
        for filter_ in self.filters.values():
            filter_.filter_set = self

    def get_base_query(self) -> dict[str, Any]:
        return copy.copy(self.__base_query)

    @classmethod
    def get_filters(cls) -> dict[str, BaseFilter]:
        """Get Filters of this FilterSet"""
        filters: dict[str, BaseFilter] = OrderedDict()
        filters.update(cls._declared_filters)
        return filters

    def filter_query(self, params: dict[str, Any]) -> dict[str, Any]:
        """Build filtration query."""
        query = self.get_base_query()
        for name, value in params.items():
            if name not in self.filters:
                continue
            query = self.filters[name].filter(query, value, params)
        return query


class AsyncFilterSet(BaseFilterSet):
    ...
