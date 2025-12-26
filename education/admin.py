from django.contrib import admin
from .models import EducationalService, Course, ServiceEnrollment, Lecture, TimetableEntry


@admin.register(EducationalService)
class EducationalServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'service_type', 'instructor', 'level', 'age_group', 'capacity', 'enrolled_count', 'status', 'is_free']
    list_filter = ['service_type', 'status', 'level', 'age_group', 'is_free', 'created_at']
    search_fields = ['title', 'description', 'instructor__username', 'instructor__email']
    readonly_fields = ['enrolled_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'service_type', 'status', 'is_free', 'fee')
        }),
        ('Instructor & Schedule', {
            'fields': ('instructor', 'schedule', 'duration', 'start_date', 'end_date')
        }),
        ('Capacity & Target Audience', {
            'fields': ('capacity', 'level', 'age_group')
        }),
        ('Statistics', {
            'fields': ('enrolled_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'service', 'instructor', 'level', 'age_group', 'capacity', 'enrolled_count', 'status']
    list_filter = ['service__service_type', 'level', 'age_group', 'status', 'created_at']
    search_fields = ['title', 'description', 'service__title', 'instructor__username']
    readonly_fields = ['enrolled_count', 'created_at', 'updated_at']


@admin.register(ServiceEnrollment)
class ServiceEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'service_or_course', 'status', 'payment_status', 'payment_method', 'has_proof', 'enrollment_date']
    list_filter = ['status', 'payment_status', 'payment_method', 'enrollment_date']
    search_fields = ['user__username', 'service__title', 'course__title', 'user__email']
    autocomplete_fields = ['user', 'service', 'course']
    readonly_fields = ['proof_image']

    def has_proof(self, obj):
        return bool(obj.proof_image)
    has_proof.boolean = True

    def service_or_course(self, obj):
        if obj.course:
            return f"{obj.course.title} (Course)"
        return f"{obj.service.title} (Service)" if obj.service else "-"
    service_or_course.short_description = "Enrolled In"


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'subject', 'date_recorded', 'has_video', 'has_audio', 'created_at']
    list_filter = ['subject', 'date_recorded', 'created_at', 'instructor']
    search_fields = ['title', 'description', 'instructor__username', 'instructor__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date_recorded'
    
    def has_video(self, obj):
        return bool(obj.video_url or obj.video_file)
    has_video.boolean = True
    
    def has_audio(self, obj):
        return bool(obj.audio_file)
    has_audio.boolean = True


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'day_of_week', 'time', 'imam', 'location', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'location']
    search_fields = ['title', 'imam', 'location']
    list_editable = ['is_active', 'time']