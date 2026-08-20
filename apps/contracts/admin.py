from django.contrib import admin

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "unit", "start_date", "end_date", "monthly_rent", "total_value")
    list_filter = ("start_date", "end_date")
    search_fields = ("member__full_name", "unit__unit_number")
