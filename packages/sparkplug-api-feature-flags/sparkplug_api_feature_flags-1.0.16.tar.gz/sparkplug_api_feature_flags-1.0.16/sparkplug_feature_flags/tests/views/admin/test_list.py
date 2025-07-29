from apps.users.factories import UserFactory
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sparkplug_feature_flags.views.admin.list import ListView


class TestListView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory(is_staff=True)

    def test_list_view(self):
        request = self.factory.get("/api/feature-flags/list/")
        force_authenticate(request, user=self.user)
        response = ListView.as_view()(request)
        assert response.status_code == 200
        assert "results" in response.data
        assert "count" in response.data
