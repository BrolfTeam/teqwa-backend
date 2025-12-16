from django.contrib import admin
from .models import EducationalService, ServiceEnrollment, Lecture


@admin.register(EducationalService)
class EducationalServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'service_type', 'instructor', 'level', 'age_group', 'capacity', 'enrolled_count', 'status']
    list_filter = ['service_type', 'level', 'age_group', 'status', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    readonly_fields = ['enrolled_count', 'created_at', 'updated_at']


@admin.register(ServiceEnrollment)
class ServiceEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'status', 'payment_status', 'enrollment_date']
    list_filter = ['status', 'payment_status', 'enrollment_date']
    search_fields = ['user__username', 'service__title']


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'subject', 'date_recorded', 'created_at']
    list_filter = ['subject', 'date_recorded', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    readonly_fields = ['created_at', 'updated_at']