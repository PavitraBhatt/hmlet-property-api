from django.contrib import admin

from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("unit_number", "property", "monthly_rent", "status")
    list_filter = ("status",)
    search_fields = ("unit_number", "property__name")
