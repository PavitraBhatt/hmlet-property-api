from rest_framework import serializers

from .models import Unit


class UnitSerializer(serializers.ModelSerializer):
    property_id = serializers.IntegerField(read_only=True)
    property_name = serializers.CharField(source="property.name", read_only=True)

    class Meta:
        model = Unit
        fields = (
            "id",
            "property_id",
            "property_name",
            "unit_number",
            "monthly_rent",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate_unit_number(self, value):
        return value.strip()
