from django.urls import path
from . import views

urlpatterns = [
    path('FundFlow/', views.FundFlow, name='FundFlow'),
]