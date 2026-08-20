from django.urls import path

from .views import PropertyDetailView, PropertyListCreateView

urlpatterns = [
    path("properties", PropertyListCreateView.as_view(), name="property-list"),
    path("properties/<int:property_id>", PropertyDetailView.as_view(), name="property-detail"),
]
