from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.properties.urls")),
    path("api/", include("apps.units.urls")),
    path("api/", include("apps.members.urls")),
    path("api/", include("apps.contracts.urls")),
]
