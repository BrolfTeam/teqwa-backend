from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('lectures/', views.lecture_list, name='lecture_list'),
    path('lectures/<int:pk>/', views.lecture_detail, name='lecture_detail'),
    path('create/', views.create_service, name='create_service'),
    path('bookings/', views.all_enrollments, name='all_bookings'),
    path('my-bookings/', views.my_enrollments, name='my_bookings'),
    path('<str:pk>/', views.service_detail, name='service_detail'),
    path('<str:pk>/book/', views.enroll_service, name='book_service'),
    path('bookings/<str:enrollment_id>/status/', views.update_enrollment_status, name='update_booking_status'),
]