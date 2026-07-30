from django.urls import path
from . import views

app_name = 'vin_decoder'

urlpatterns = [
    path('', views.home, name= 'home'),
    path('get_car_issues', views.openai_common_car_issues, name= "get_car_issues"), #urls for partial too
    path('export_pdf', views.export_vin_raport_pdf, name= 'export_pdf'),
    path('check_task_status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    path('contact',views.contanct_view, name='contact')
]