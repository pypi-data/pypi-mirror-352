from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_feature_flags.factories import FeatureFlagFactory
from sparkplug_feature_flags.views.admin import GiveAccessView


class TestGiveAccessView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory(is_staff=True)
        self.feature_flag = FeatureFlagFactory()

    def test_give_access(self):
        request = self.factory.patch(
            f"/api/feature-flags/{self.feature_flag.uuid}/give-access/",
            data={"user_uuid": self.user.uuid},
        )
        force_authenticate(request, user=self.user)
        response = GiveAccessView.as_view()(
            request, uuid=self.feature_flag.uuid
        )
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert "uuid" in response.data[0]
