from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.views.admin import DetailView


class TestDetailView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory(is_staff=True)
        self.feature_flag = FeatureFlagFactory()

    def test_get_detail(self):
        request = self.factory.get(
            f"/api/feature-flags/{self.feature_flag.uuid}/"
        )
        force_authenticate(request, user=self.user)
        response = DetailView.as_view()(request, uuid=self.feature_flag.uuid)
        assert response.status_code == 200
        assert response.data["uuid"] == str(self.feature_flag.uuid)
        assert response.data["title"] == self.feature_flag.title
