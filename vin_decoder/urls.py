from django.urls import path
from . import views

app_name = 'vin_decoder'

urlpatterns = [
    path('', views.home, name= 'home'),
    path('get_car_issues', views.openai_get_car_info, name= "get_car_issues") #urls for partial too
]