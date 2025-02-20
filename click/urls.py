from django.urls import path
from .views import *




urlpatterns = [
    path('', CreateClickOrderView.as_view()),
    path('click/transaction/', OrderTestView.as_view()),
]