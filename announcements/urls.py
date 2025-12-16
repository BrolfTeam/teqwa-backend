from django.urls import path
from . import views

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'),
    path('create/', views.create_announcement, name='create_announcement'),
    path('<str:pk>/', views.announcement_detail, name='announcement_detail'),
    path('<str:pk>/update/', views.update_announcement, name='update_announcement'),
    path('<str:pk>/delete/', views.delete_announcement, name='delete_announcement'),
]