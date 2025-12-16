from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('create/', views.create_staff, name='create_staff'),
    path('attendance/', views.staff_attendance, name='staff_attendance'),
    path('attendance/toggle/', views.toggle_attendance, name='toggle_attendance'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    path('working-hours/', views.working_hours, name='working_hours'),
    path('tasks/', views.staff_tasks, name='staff_tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<str:task_id>/status/', views.update_task_status, name='update_task_status'),
    path('reports/', views.staff_reports, name='staff_reports'),
    path('<str:pk>/', views.staff_detail, name='staff_detail'),
    path('<str:pk>/update/', views.update_staff, name='update_staff'),
]