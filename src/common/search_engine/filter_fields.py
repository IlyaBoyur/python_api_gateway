import abc
from collections.abc import Sequence
from typing import Any, Literal, NamedTuple

from pydantic import BaseModel


class BaseFilter(abc.ABC):
    def __init__(
        self,
        field_name: Any | None = None,
    ) -> None:
        super().__init__()
        self.field_name = field_name

    @abc.abstractmethod
    def filter(self, query: dict[str, Any], value: Any, params: dict[str, Any]) -> dict[str, Any]:
        ...


class Filter(BaseFilter):
    def filter(
        self,
        query: dict[str, Any],
        value: Any,
        _: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply filtering by 'must'.
        :param query: query object
        :param value: value for field to have in filtered out objects

        :returns: query after the provided filtering has been applied
        """
        must_clauses = query.get("query", {}).get("bool", {}).get("must", [])
        must_clauses.append({"term": {self.field_name: value}})
        query["query"] = query.get("query", {})
        query["query"]["bool"] = query["query"].get("bool", {})
        query["query"]["bool"]["must"] = must_clauses
        return query


class InFilter(BaseFilter):
    def filter(
        self,
        query: dict[str, Any],
        value: Sequence[str],
        _: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply filtering by 'terms'.

        :param query: query object
        :param value: sequence of values for field to have in filtered out objects

        :returns: query after the provided filtering has been applied
        """
        must_clauses = query.get("query", {}).get("bool", {}).get("must", [])
        must_clauses.append({"terms": {self.field_name: value}})
        query["query"] = query.get("query", {})
        query["query"]["bool"] = query["query"].get("bool", {})
        query["query"]["bool"]["must"] = must_clauses
        return query


class NotInFilter(BaseFilter):
    def filter(
        self,
        query: dict[str, Any],
        value: Sequence[str],
        _: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply exclusion filtering by 'terms'.

        :param query: query object
        :param value: sequence of values for field to not have in filtered out objects

        :returns: query after the provided filtering has been applied
        """
        must_not_clauses = query.get("query", {}).get("bool", {}).get("must_not", [])
        must_not_clauses.append({"terms": {self.field_name: value}})
        query["query"] = query.get("query", {})
        query["query"]["bool"] = query["query"].get("bool", {})
        query["query"]["bool"]["must_not"] = must_not_clauses
        return query


class RangeFilter(BaseFilter):
    def filter(
        self,
        query: dict[str, Any],
        value: tuple[Any, Any] | None,
        _: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply filtering by 'range'.

        :param query: query object
        :param value: tuple of lower and upper bounds for inclusive range

        :returns: query after the provided range has been applied
        """
        if not value:
            return query
        left_value, right_value = value

        filters = {}
        if left_value is not None:
            filters.update({"gte": left_value})
        if right_value is not None:
            filters.update({"lte": right_value})
        if filters:
            must_clauses = query.get("query", {}).get("bool", {}).get("must", [])
            must_clauses.append({"range": {self.field_name: filters}})
            query["query"] = query.get("query", {})
            query["query"]["bool"] = query["query"].get("bool", {})
            query["query"]["bool"]["must"] = must_clauses
        return query


class SearchFilter(BaseFilter):
    def filter(
        self,
        query: dict[str, Any],
        value: Any,
        _: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply filtering by 'match'.

        :param query: query object
        :param value: pattern to be searched for with 'match' query

        :returns: query after the provided search pattern has been applied
        """
        must_clauses = query.get("query", {}).get("bool", {}).get("must", [])
        must_clauses.append({"match": {self.field_name: value}})
        query["query"] = query.get("query", {})
        query["query"]["bool"] = query["query"].get("bool", {})
        query["query"]["bool"]["must"] = must_clauses
        return query


class OrderingField(NamedTuple):
    field: str


class OrderingFilter(BaseFilter):
    def __init__(self, **fields: OrderingField) -> None:
        """Init.
        :param fields: available for future ordering fields

        Example:
            ordering_filter = OrderingFilter(
                area=OrderingField("area"),
                title=OrderingField("title"),
                id=OrderingField("id")
            )

        """
        super().__init__()
        self.fields: dict[str, OrderingField] = fields

    def filter(
        self, query: dict[str, Any], value: Sequence[str], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply ordering to a query instance.

        :param query: query for ordering
        :param value:
            A sequence of strings, where each one specify
            which ordering field from available `self.fields` should be applied
            Also specify ordering direction

        :returns: query after the provided ordering has been applied
        """
        if not value:
            return query

        ordering_fields = self._get_actual_fields(value)
        if ordering_fields:
            sort = query.get("sort", [])
            sort.extend(ordering_fields)
            query["sort"] = sort
        return query

    def _get_actual_fields(self, value: Sequence[str]) -> list[dict]:
        """Get ES fields from provided ordering fields.
        :param value:
            A sequence of strings, where each one specify
            which ordering field from available `self.fields` should be applied
            Also specify ordering direction

        :returns: fields to be used for ordering
        """
        actual_fields = []
        for field in value:
            if field.startswith("-"):
                field = field[1:]
                direction = "desc"
            else:
                direction = "asc"
            if field in self.fields:
                actual_fields.append({self.fields[field].field: {"order": direction}})
        return actual_fields


class LimitOffsetFilter(BaseFilter):
    def filter(
        self,
        query: dict[str, Any],
        value: tuple[int | None, int | None] | None,
        _: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply limit offset pagination to a query instance.

        :param query: query for pagination
        :param value: A tuple of positive integers (limit, offset)

        :returns: query after the provided pagination has been applied
        """
        if not value:
            return query

        offset, limit = value
        if limit:
            query["size"] = limit
        if offset:
            query["from"] = offset
        return query
