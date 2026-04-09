from django.urls import path
from . import views

app_name = 'vin_decoder'

urlpatterns = [
    path('', views.home, name= 'home'),
    path('get_car_issues', views.get_vehicle_data_vin, name= "get_car_issues") #urls for partial too
]