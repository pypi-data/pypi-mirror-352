from django.conf import settings
from django.db import models
from sparkplug_core.models import (
    BaseModel,
    SubscriberMixin,
)


class FeatureFlag(
    SubscriberMixin,
    BaseModel,
):
    # User --< FeatureFlag
    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        default="",
        blank=True,
    )

    enabled = models.BooleanField(
        default=True,
    )

    # User >--< FeatureFlag
    users = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        through="FlagAccess",
        related_name="feature_flags",
    )

    subscription_key = "featureFlags"

    class Meta:
        indexes = (models.Index(fields=["uuid"]),)

    def __str__(self) -> str:
        return self.title
