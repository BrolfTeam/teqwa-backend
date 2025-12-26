from django.urls import path
from . import views

urlpatterns = [
    path('', views.donation_list, name='donation_list'),
    path('create/', views.create_donation, name='create_donation'),
    path('causes/', views.donation_causes, name='donation_causes'),
    path('causes/create/', views.create_cause, name='create_cause'),
    path('causes/<int:cause_id>/', views.cause_detail, name='cause_detail'),
    path('stats/', views.donation_stats, name='donation_stats'),
]