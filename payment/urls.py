from django.urls import path
from .views import *




urlpatterns = [
    path('pay/', PaymentView.as_view(), name='payment'),
    #path('pay/<str:transaction_id>/', PaymentView.as_view(), name='payment-update'),
    path('webhook/payze/success/', payze_webhook, name='payze-webhook'),
]