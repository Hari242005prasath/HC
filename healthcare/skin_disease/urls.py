from django.urls import path
from .views import generate_skin_report,myself

urlpatterns = [
    path('generate_skin_report', generate_skin_report, name='generate_skin_report'),
    path('home', myself, name='home'),

]
