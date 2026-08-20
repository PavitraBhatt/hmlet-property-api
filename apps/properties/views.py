from django.db.models import Count
from rest_framework import generics

from .models import Property
from .serializers import PropertyDetailSerializer, PropertySerializer


class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer

    def get_queryset(self):
        queryset = Property.objects.annotate(units_count=Count("units"))
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PropertyDetailView(generics.RetrieveAPIView):
    serializer_class = PropertyDetailSerializer
    lookup_url_kwarg = "property_id"
    queryset = Property.objects.annotate(units_count=Count("units")).prefetch_related(
        "units__property"
    )
