from collections import OrderedDict

import pytest

from src.common.search_engine.filter_fields import (
    Filter,
    InFilter,
    LimitOffsetFilter,
    NotInFilter,
    OrderingField,
    OrderingFilter,
    RangeFilter,
    SearchFilter,
)


class TestFilter:
    def test_filter_adds_term_clause(self):
        """Ensure 'Filter' adds a term clause to the query"""
        f = Filter(field_name="status")
        result = f.filter({}, "active", {})
        assert result == {"query": {"bool": {"must": [{"term": {"status": "active"}}]}}}


class TestInFilter:
    def test_filter_adds_terms_clause(self):
        """Ensure 'InFilter' adds a terms clause for field"""
        f = InFilter(field_name="category")
        result = f.filter({}, ["a", "b"], {})
        assert result == {"query": {"bool": {"must": [{"terms": {"category": ["a", "b"]}}]}}}


class TestNotInFilter:
    def test_filter_adds_terms_must_not_clause(self):
        """Ensure 'NotInFilter' adds exclusion clause with 'must_not'"""
        f = NotInFilter(field_name="status")
        result = f.filter({}, ["archived"], {})
        assert result == {"query": {"bool": {"must_not": [{"terms": {"status": ["archived"]}}]}}}


class TestRangeFilter:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ((5, 10), {"range": {"price": {"gte": 5, "lte": 10}}}),
            ((None, 10), {"range": {"price": {"lte": 10}}}),
            ((5, None), {"range": {"price": {"gte": 5}}}),
        ],
    )
    def test_filter_range(self, value, expected):
        """Ensure RangeFilter correctly constructs 'range' clauses"""
        f = RangeFilter(field_name="price")
        result = f.filter({}, value, {})
        assert expected in result.get("query", {}).get("bool", {}).get("must", [])

    def test_filter_skips_when_none(self):
        """If value is None, RangeFilter should return original query"""
        f = RangeFilter(field_name="price")
        query = {"query": {"bool": {"must": [{"some": "thing"}]}}}
        assert f.filter(query.copy(), None, {}) == query


class TestSearchFilter:
    def test_filter_match_clause(self):
        """Ensure SearchFilter appends a 'match' clause"""
        f = SearchFilter(field_name="title")
        result = f.filter({}, "search_term", {})
        assert result == {"query": {"bool": {"must": [{"match": {"title": "search_term"}}]}}}


class TestOrderingFilter:
    def test_ordering_filter_asc_desc(self):
        """OrderingFilter maps values to correct sort clauses"""
        ordering = OrderingFilter(name=OrderingField("user.name"), age=OrderingField("user.age"))
        query = ordering.filter({}, ["-age", "name"], {})
        assert query["sort"] == [{"user.age": {"order": "desc"}}, {"user.name": {"order": "asc"}}]

    def test_ignores_invalid_fields(self):
        """Invalid ordering fields are ignored"""
        ordering = OrderingFilter(name=OrderingField("name"))
        query = ordering.filter({}, ["invalid_field"], {})
        assert query.get("sort") is None

    def test_adds_only_valid_fields(self):
        """Invalid ordering fields are ignored"""
        ordering = OrderingFilter(name=OrderingField("name"))
        query = ordering.filter({}, ["invalid_field", "name"], {})
        assert query["sort"] == [{"name": {"order": "asc"}}]


class TestLimitOffsetFilter:
    def test_pagination_filter_applies_limit_offset(self):
        """Ensure LimitOffsetFilter sets 'size' and 'from'"""
        f = LimitOffsetFilter(field_name=None)
        result = f.filter({}, (2, 100), {})
        assert result == {"size": 100, "from": 2}

    def test_pagination_skips_if_none(self):
        """Should return original query if value is None"""
        f = LimitOffsetFilter(field_name=None)
        query = {"query": {"bool": {}}}
        assert f.filter(query.copy(), None, {}) == query
