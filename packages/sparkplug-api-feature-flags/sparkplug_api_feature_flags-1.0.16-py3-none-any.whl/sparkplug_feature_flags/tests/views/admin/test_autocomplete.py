from unittest.mock import patch

from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.views.admin import AutocompleteView


class TestAutocompleteView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory(is_staff=True)

    @patch(
        "sparkplug_feature_flags.views.admin.autocomplete.feature_flag_autocomplete"
    )
    def test_autocomplete_view_success(self, mock_feature_flag_autocomplete):
        feature_flag = FeatureFlagFactory()
        feature_flag_dict = {
            "uuid": feature_flag.uuid,
            "created": feature_flag.created,
            "title": feature_flag.title,
            "description": feature_flag.description,
            "enabled": feature_flag.enabled,
        }

        mock_feature_flag_autocomplete.return_value = [feature_flag_dict]

        request = self.factory.get(
            "/api/feature-flags/autocomplete/?term=test&page=1"
        )
        force_authenticate(request, user=self.user)
        response = AutocompleteView.as_view()(request)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == feature_flag.title
        assert response.data[0]["uuid"] == feature_flag.uuid

    @patch(
        "sparkplug_feature_flags.views.admin.autocomplete.feature_flag_autocomplete"
    )
    def test_autocomplete_view_empty_results(
        self, mock_feature_flag_autocomplete
    ):
        mock_feature_flag_autocomplete.return_value = []
        request = self.factory.get(
            "/api/feature-flags/autocomplete/?term=unknown&page=1"
        )
        force_authenticate(request, user=self.user)
        response = AutocompleteView.as_view()(request)
        assert response.status_code == 200
        assert response.data == []

    @patch(
        "sparkplug_feature_flags.views.admin.autocomplete.feature_flag_autocomplete"
    )
    def test_autocomplete_view_unauthenticated(
        self, mock_feature_flag_autocomplete
    ):
        mock_feature_flag_autocomplete.return_value = []
        request = self.factory.get(
            "/api/feature-flags/autocomplete/?term=test&page=1"
        )
        response = AutocompleteView.as_view()(request)
        assert response.status_code == 401
