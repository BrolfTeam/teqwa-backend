from django.urls import path
from . import views

urlpatterns = [
    path('slots/', views.slot_list, name='slot_list'),
    path('slots/create/', views.create_slot, name='create_slot'),
    path('slots/<str:pk>/', views.slot_detail, name='slot_detail'),
    path('slots/<str:pk>/book/', views.book_slot, name='book_slot'),
    path('bookings/', views.all_bookings, name='all_bookings'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<str:booking_id>/status/', views.update_booking_status, name='update_booking_status'),
]