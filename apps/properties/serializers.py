from rest_framework import serializers

from apps.units.serializers import UnitSerializer

from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    units_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Property
        fields = ("id", "name", "address", "units_count", "created_at", "updated_at")
        read_only_fields = ("id", "units_count", "created_at", "updated_at")


class PropertyDetailSerializer(PropertySerializer):
    """Detail view carries the units so the client does not need a second call."""

    units = UnitSerializer(many=True, read_only=True)

    class Meta(PropertySerializer.Meta):
        fields = PropertySerializer.Meta.fields + ("units",)
