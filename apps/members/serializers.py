from rest_framework import serializers

from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ("id", "full_name", "email", "phone", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_email(self, value):
        return value.lower().strip()
