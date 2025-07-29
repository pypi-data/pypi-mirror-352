from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.views.admin import SetEnabledView


class TestSetEnabledView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory(is_staff=True)
        self.feature_flag = FeatureFlagFactory(enabled=False)

    def test_set_enabled(self):
        request = self.factory.patch(
            f"/api/feature-flags/{self.feature_flag.uuid}/set-enabled/",
            data={"enabled": True},
        )
        force_authenticate(request, user=self.user)
        response = SetEnabledView.as_view()(
            request, uuid=self.feature_flag.uuid
        )
        assert response.status_code == 200
        assert response.data["enabled"] is True
