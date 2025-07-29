from rest_framework import serializers
from rest_framework.serializers import Serializer

from .feature_flag import FeatureFlagSerializer


class FlagAccessSerializer(Serializer):
    uuid = serializers.CharField()
    feature_flag_uuid = serializers.SerializerMethodField()
    feature_flag = FeatureFlagSerializer()
    user_uuid = serializers.SerializerMethodField()

    def get_feature_flag_uuid(self, obj):
        return obj.feature_flag.uuid

    def get_user_uuid(self, obj):
        return obj.user.uuid
