from typing import ClassVar

from django_elasticsearch_dsl import (
    Document,
    fields,
)
from django_elasticsearch_dsl.registries import registry
from sparkplug_core.search import analyzers

from .. import models


@registry.register_document
class FeatureFlag(Document):
    uuid = fields.KeywordField()

    title = fields.TextField(
        analyzer="standard",
        fields={
            "raw": fields.Keyword(),
            "edge_ngram": fields.TextField(
                analyzer=analyzers.edge_ngram,
            ),
            "trigram": fields.TextField(
                analyzer=analyzers.trigram,
            ),
        },
    )

    class Index:
        name = "feature-flags"

        settings: ClassVar = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = models.FeatureFlag
