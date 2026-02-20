from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('history/', views.history, name='history'),   # 👈 VERY IMPORTANT
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]