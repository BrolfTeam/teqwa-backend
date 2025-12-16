from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('sessions/', views.user_sessions, name='user_sessions'),
    path('sessions/<str:session_id>/terminate/', views.terminate_session, name='terminate_session'),
    path('sessions/terminate-all/', views.terminate_all_sessions, name='terminate_all_sessions'),
    path('activities/', views.user_activities, name='user_activities'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('dashboard-stats/', views.user_dashboard_stats, name='user_dashboard_stats'),
    path('users/', views.user_list, name='user_list'),
    path('users/<str:pk>/', views.user_detail, name='user_detail'),
]