from src.common.search_engine.filtersets import BaseFilterSet
from src.common.search_engine.filter_fields import (
    Filter,
    InFilter,
    NotInFilter,
    RangeFilter,
    SearchFilter,
    LimitOffsetFilter,
    OrderingField,
    OrderingFilter,
)


class SampleFilterSet(BaseFilterSet):
    status = Filter()
    tags = InFilter()
    ids = NotInFilter()
    age = RangeFilter()
    name = SearchFilter()
    order = OrderingFilter(
        fields={
            "created_at": OrderingField("created_at"),
            "updated_at": OrderingField("updated_at"),
        },
    )
    pagination = LimitOffsetFilter()


class TestFilterSet:
    def test_declared_filters_bound_correctly(self):
        """Ensure filters are bound and field_name is auto-inferred"""
        fs = SampleFilterSet()
        assert set(fs.filters) == {"status", "tags", "ids", "age", "name", "order", "pagination"}
        assert fs.filters["status"].field_name == "status"

    def test_filter_query_applies_all_filters(self):
        """Check filter_query applies multiple filters in sequence"""
        fs = SampleFilterSet()
        result = fs.filter_query(
            {"status": "active", "tags": ["t1", "t2"], "age": (18, 30), "name": "john"}
        )

        must = result["query"]["bool"]["must"]
        assert {"term": {"status": "active"}} in must
        assert {"terms": {"tags": ["t1", "t2"]}} in must
        assert {"range": {"age": {"gte": 18, "lte": 30}}} in must
        assert {"match": {"name": "john"}} in must

    def test_ignores_unknown_filter_param(self):
        """Ensure unknown filter params are ignored silently"""
        fs = SampleFilterSet()
        result = fs.filter_query({"nonexistent": "x"})
        assert result == {}
