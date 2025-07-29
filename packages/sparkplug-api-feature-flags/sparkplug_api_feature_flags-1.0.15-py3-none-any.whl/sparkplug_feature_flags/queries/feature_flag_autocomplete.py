from django.db.models import QuerySet
from elasticsearch_dsl.query import Q
from sparkplug_core.serializers import SearchTermData

from .. import documents, models


def feature_flag_autocomplete(
    filters: SearchTermData,
) -> QuerySet[models.FeatureFlag]:
    """Return a QuerySet based on the Elasticsearch autocomplete query."""
    search = documents.FeatureFlag.search()
    q = Q("match", title__edge_ngram=filters.term)
    search = search.query(q)
    search = search[filters.start : filters.end]
    return search.to_queryset()
