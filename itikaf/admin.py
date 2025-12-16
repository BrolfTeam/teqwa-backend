from django.contrib import admin
from django.utils.html import format_html
from .models import ItikafProgram, ItikafSchedule, ItikafRegistration
from authentication.utils import send_itikaf_approval_email


@admin.register(ItikafProgram)
class ItikafProgramAdmin(admin.ModelAdmin):
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set organizer for new objects
            obj.organizer = request.user
        super().save_model(request, obj, form, change)
    list_display = ['title', 'start_date', 'end_date', 'status', 'capacity', 'get_participant_count', 'get_registration_status']
    list_filter = ['status', 'gender_restriction', 'is_free', 'start_date']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at', 'get_participant_count', 'get_registration_status', 'get_is_full']
    
    def get_participant_count(self, obj):
        """Safely get participant count"""
        try:
            return obj.participant_count
        except Exception:
            return 0
    get_participant_count.short_description = 'Participants'
    
    def get_registration_status(self, obj):
        """Safely get registration status"""
        try:
            if obj.is_registration_open:
                return format_html('<span style="color: green;">Open</span>')
            elif obj.is_full:
                return format_html('<span style="color: orange;">Full</span>')
            else:
                return format_html('<span style="color: red;">Closed</span>')
        except Exception:
            return 'Unknown'
    get_registration_status.short_description = 'Registration'
    
    def get_is_full(self, obj):
        """Safely check if full"""
        try:
            return obj.is_full
        except Exception:
            return False
    get_is_full.short_description = 'Is Full'
    get_is_full.boolean = True
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'short_description')
        }),
        ('Dates and Timing', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Location and Capacity', {
            'fields': ('location', 'capacity', 'gender_restriction')
        }),
        ('Program Details', {
            'fields': ('fee', 'is_free', 'requirements', 'what_to_bring')
        }),
        ('Status and Media', {
            'fields': ('status', 'image', 'image_url')
        }),
        ('Statistics', {
            'fields': ('get_participant_count', 'get_registration_status', 'get_is_full'),
            'description': 'These are calculated values based on registrations and program status'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItikafSchedule)
class ItikafScheduleAdmin(admin.ModelAdmin):
    list_display = ['program', 'date', 'day_number']
    list_filter = ['program', 'date']
    search_fields = ['program__title', 'notes']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ItikafRegistration)
class ItikafRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'program', 'status', 'payment_status', 'registered_at']
    list_filter = ['status', 'payment_status', 'registered_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'program__title']
    readonly_fields = ['registered_at', 'confirmed_at', 'cancelled_at']
    
    def save_model(self, request, obj, form, change):
        """Override to send email when status changes"""
        if change:
            # Get old status before saving
            old_obj = ItikafRegistration.objects.get(pk=obj.pk)
            old_status = old_obj.status
            super().save_model(request, obj, form, change)
            # Send email if status changed
            if old_status != obj.status and obj.status in ['confirmed', 'approved', 'rejected', 'waitlisted']:
                try:
                    send_itikaf_approval_email(obj, obj.program, obj.user, status=obj.status)
                except Exception as e:
                    print(f"Error sending iʿtikāf status change email: {e}")
        else:
            super().save_model(request, obj, form, change)
