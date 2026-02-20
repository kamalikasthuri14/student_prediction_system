from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('history/', views.history, name='history'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),

    # EDIT & DELETE
    path('edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),
]