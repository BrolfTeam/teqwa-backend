from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventRegistration
from .forms import EventAdminForm


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ['title', 'image_preview', 'date', 'location', 'capacity', 'attendee_count', 'status']
    list_filter = ['status', 'date']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['attendee_count', 'image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'image', 'image_url', 'image_preview'),
            'description': 'You can either upload an image file OR provide an external image URL (not both)'
        }),
        ('Schedule', {
            'fields': ('date', 'end_date', 'location')
        }),
        ('Capacity & Status', {
            'fields': ('capacity', 'attendee_count', 'status')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        image_url = obj.get_image_url()
        if image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', image_url)
        return "No image"
    image_preview.short_description = 'Image'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'registered_at']
    list_filter = ['status', 'registered_at']
    search_fields = ['user__username', 'event__title']