from django.contrib import admin
from .models import *




@admin.register(ClickOrder)
class ClickTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "amount",
        "is_paid",
    )
    list_display_links = ("id", "amount", 'is_paid')

    search_fields = ["id", 'is_paid']
    save_on_top = True
