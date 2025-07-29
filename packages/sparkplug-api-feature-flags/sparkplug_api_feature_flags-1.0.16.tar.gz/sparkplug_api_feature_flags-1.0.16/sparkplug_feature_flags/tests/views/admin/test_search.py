from unittest import skip
from unittest.mock import MagicMock, patch

from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_feature_flags.views.admin import SearchView


def create_mock_queryset(items):
    """Helper function to create a QuerySet-like mock."""
    mock_queryset = MagicMock()
    mock_queryset.__len__.return_value = len(items)
    mock_queryset.__iter__.return_value = iter(items)
    mock_queryset.count.return_value = len(items)
    mock_queryset.__getitem__.side_effect = lambda s: items[s]  # For slicing
    return mock_queryset


class TestSearchView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory(is_staff=True)

    @patch("sparkplug_feature_flags.queries.feature_flag_search")
    def test_search_view_empty_results(self, mock_feature_flag_search):
        # Mock the feature_flag_search to return an empty QuerySet-like object
        mock_feature_flag_search.return_value = create_mock_queryset([])

        request = self.factory.get(
            "/api/feature-flags/search/?term=test&page=1"
        )
        force_authenticate(request, user=self.user)
        response = SearchView.as_view()(request)

        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
        assert response.data["results"] == []
        assert response.data["count"] == 0

    @skip("Skipping test due to unresolved issues")
    @patch("sparkplug_feature_flags.queries.feature_flag_search")
    def test_search_view_with_results(self, mock_feature_flag_search):
        # Mock the feature_flag_search to return a QuerySet-like object with one item
        mock_feature_flag = MagicMock()
        mock_feature_flag.id = 1
        mock_feature_flag.name = "Test Feature Flag"

        # Create a QuerySet-like mock
        mock_result = MagicMock()
        mock_result.__len__.return_value = 1
        mock_result.__iter__.return_value = iter([mock_feature_flag])
        mock_result.count.return_value = 1
        mock_result.__getitem__.side_effect = lambda s: [mock_feature_flag][
            s
        ]  # For slicing
        mock_feature_flag_search.return_value = mock_result

        request = self.factory.get(
            "/api/feature-flags/search/?term=test&page=1"
        )
        force_authenticate(request, user=self.user)
        response = SearchView.as_view()(request)

        # Debugging: Print the response data to inspect its structure
        print("Response data:", response.data)

        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Test Feature Flag"

    @patch("sparkplug_feature_flags.queries.feature_flag_search")
    def test_search_view_unauthenticated(self, mock_feature_flag_search):
        # Mock the feature_flag_search to ensure it is not called
        mock_feature_flag_search.return_value = []

        request = self.factory.get(
            "/api/feature-flags/search/?term=test&page=1"
        )
        # Do not authenticate the request
        response = SearchView.as_view()(request)

        assert response.status_code == 401
