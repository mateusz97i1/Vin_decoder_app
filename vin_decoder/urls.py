from django.urls import path
from . import views

app_name = 'vin_decoder'

urlpatterns = [
    path('', views.home, name= 'home')
]