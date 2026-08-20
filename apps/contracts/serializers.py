from rest_framework import serializers

from apps.members.models import Member
from apps.units.models import Unit

from .models import Contract


class ContractMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ("id", "full_name", "email")


class ContractUnitSerializer(serializers.ModelSerializer):
    property_id = serializers.IntegerField(read_only=True)
    property_name = serializers.CharField(source="property.name", read_only=True)

    class Meta:
        model = Unit
        fields = ("id", "unit_number", "status", "property_id", "property_name")


class ContractSerializer(serializers.ModelSerializer):
    member = ContractMemberSerializer(read_only=True)
    unit = ContractUnitSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Contract
        fields = (
            "id",
            "member",
            "unit",
            "start_date",
            "end_date",
            "monthly_rent",
            "total_value",
            "is_active",
            "created_at",
            "updated_at",
        )


class ContractCreateSerializer(serializers.Serializer):
    member_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), source="member")
    unit_id = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), source="unit")
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    monthly_rent = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, required=False, allow_null=True
    )

    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError(
                {"end_date": "end_date must be on or after start_date."}
            )
        return attrs
