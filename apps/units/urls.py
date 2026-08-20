from django.urls import path

from .views import PropertyUnitListCreateView, UnitListView

urlpatterns = [
    path("units", UnitListView.as_view(), name="unit-list"),
    path(
        "properties/<int:property_id>/units",
        PropertyUnitListCreateView.as_view(),
        name="property-unit-list",
    ),
]
