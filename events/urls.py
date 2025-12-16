from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<str:pk>/', views.event_detail, name='event_detail'),
    path('<str:pk>/register/', views.register_for_event, name='register_for_event'),
    path('<str:pk>/unregister/', views.unregister_from_event, name='unregister_from_event'),
    path('<str:pk>/attendees/', views.event_attendees, name='event_attendees'),
]