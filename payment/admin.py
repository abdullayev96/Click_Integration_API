from django.contrib import admin
from .models import *


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id', 'amount','card_number', 'transaction_id',  'status', 'created_at']

    list_filter = ['id','card_number', 'amount']

    search_fields = ['card_number', 'order_id']



admin.site.register(Payment, PaymentAdmin)