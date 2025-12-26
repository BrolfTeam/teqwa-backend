from django.urls import path
from . import views

urlpatterns = [
    # Services
    path('', views.service_list, name='service_list'),
    path('create/', views.create_service, name='create_service'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    
    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    
    # Enrollments
    path('<int:pk>/book/', views.enroll_service, name='book_service'),
    path('courses/<int:pk>/book/', views.enroll_service, name='book_course'),
    path('bookings/', views.all_enrollments, name='all_bookings'),
    path('my-bookings/', views.my_enrollments, name='my_bookings'),
    path('bookings/<str:enrollment_id>/status/', views.update_enrollment_status, name='update_booking_status'),
    
    # Lectures
    path('lectures/', views.lecture_list, name='lecture_list'),
    path('lectures/<int:pk>/', views.lecture_detail, name='lecture_detail'),
]