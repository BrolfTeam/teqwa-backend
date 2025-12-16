from django.urls import path
from . import views

urlpatterns = [
    # Program endpoints
    path('', views.program_list, name='itikaf_program_list'),
    path('create/', views.create_program, name='create_itikaf_program'),
    path('my-registrations/', views.my_registrations, name='my_itikaf_registrations'),
    path('<str:pk>/', views.program_detail, name='itikaf_program_detail'),
    path('<str:pk>/schedules/', views.program_schedules, name='itikaf_program_schedules'),
    path('<str:pk>/participants/', views.program_participants, name='itikaf_program_participants'),
    
    # Registration endpoints
    path('<str:pk>/register/', views.register_for_program, name='register_for_itikaf'),
    path('<str:pk>/unregister/', views.unregister_from_program, name='unregister_from_itikaf'),
    path('registrations/<int:registration_id>/status/', views.update_registration_status, name='update_itikaf_registration_status'),
    
    # Schedule endpoints
    path('<str:pk>/schedules/create/', views.create_schedule, name='create_itikaf_schedule'),
]

