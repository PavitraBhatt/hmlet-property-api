from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers

from apps.properties.models import Property

from .models import Unit, UnitStatus
from .serializers import UnitSerializer


class UnitListView(generics.ListAPIView):
    """GET /api/units - flat list across every property, filterable."""

    serializer_class = UnitSerializer

    def get_queryset(self):
        queryset = Unit.objects.select_related("property")

        status = self.request.query_params.get("status")
        if status:
            if status not in UnitStatus.values:
                raise serializers.ValidationError(
                    {"status": f"Must be one of: {', '.join(UnitStatus.values)}."}
                )
            queryset = queryset.filter(status=status)

        property_id = self.request.query_params.get("property_id")
        if property_id:
            queryset = queryset.filter(property_id=property_id)

        return queryset


class PropertyUnitListCreateView(generics.ListCreateAPIView):
    """POST/GET /api/properties/:property_id/units"""

    serializer_class = UnitSerializer

    def get_property(self):
        return get_object_or_404(Property, pk=self.kwargs["property_id"])

    def get_queryset(self):
        return Unit.objects.select_related("property").filter(
            property_id=self.get_property().pk
        )

    def perform_create(self, serializer):
        prop = self.get_property()
        unit_number = serializer.validated_data["unit_number"]

        if Unit.objects.filter(property=prop, unit_number=unit_number).exists():
            raise serializers.ValidationError(
                {"unit_number": f"Unit '{unit_number}' already exists in this property."}
            )

        serializer.save(property=prop)
