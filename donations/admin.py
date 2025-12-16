from django.contrib import admin
from .models import Donation, DonationCause


@admin.register(DonationCause)
class DonationCauseAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_amount', 'raised_amount', 'progress_percentage', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['progress_percentage', 'created_at', 'updated_at']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'amount', 'cause', 'method', 'status', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['donor_name', 'email']
    readonly_fields = ['created_at', 'updated_at']