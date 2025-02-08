from django.urls import path
from .views import generate_skin_report

urlpatterns = [
    path('generate_skin_report', generate_skin_report, name='generate_skin_report'),
]
