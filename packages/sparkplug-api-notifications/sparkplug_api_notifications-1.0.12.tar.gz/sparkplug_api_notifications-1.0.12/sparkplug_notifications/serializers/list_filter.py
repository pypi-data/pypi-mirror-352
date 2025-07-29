from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer


@dataclass
class ListFilterData:
    recipient: AbstractBaseUser
    has_read: Optional[bool] = None
    is_starred: Optional[bool] = None


class ListFilterSerializer(DataclassSerializer):
    recipient = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )

    class Meta:
        dataclass = ListFilterData
