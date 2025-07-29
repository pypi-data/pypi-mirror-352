from unittest.mock import MagicMock, patch

from django.test import TestCase
from elasticsearch_dsl.query import Match
from sparkplug_core.serializers import SearchTermData

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.models import FeatureFlag
from sparkplug_feature_flags.queries import feature_flag_search


class TestFeatureFlagSearch(TestCase):
    def setUp(self):
        # Create some FeatureFlag instances using factories
        self.feature_flag_1 = FeatureFlagFactory(title="Feature A")
        self.feature_flag_2 = FeatureFlagFactory(title="Feature B")

    @patch(
        "sparkplug_feature_flags.queries.feature_flag_search.documents.FeatureFlag.search"
    )
    def test_feature_flag_search(self, mock_search):
        # Mock Elasticsearch search behavior
        mock_search_instance = MagicMock()
        mock_search.return_value = mock_search_instance

        # Mock the query results
        mock_search_instance.query.return_value = mock_search_instance
        mock_search_instance.__getitem__.return_value = mock_search_instance
        mock_search_instance.to_queryset.return_value = (
            FeatureFlag.objects.filter(
                id__in=[self.feature_flag_1.id, self.feature_flag_2.id]
            )
        )

        # Define filters
        filters = SearchTermData(term="Feature", page=1)

        # Call the function
        result = feature_flag_search(filters)

        # Assertions
        mock_search.assert_called_once()
        mock_search_instance.query.assert_called_once_with(
            Match(title__trigram="Feature")
        )
        assert result.count() == 2
        assert self.feature_flag_1 in result
        assert self.feature_flag_2 in result
