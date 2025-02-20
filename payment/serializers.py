from rest_framework import serializers
from .models import Payment





class PaymentRequestSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=255)
    amount = serializers.IntegerField()



