from django.contrib import admin
from .models import FutsalSlot, FutsalBooking


@admin.register(FutsalSlot)
class FutsalSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'location', 'price', 'available']
    list_filter = ['date', 'location', 'available']
    search_fields = ['location']
    readonly_fields = ['created_at']


@admin.register(FutsalBooking)
class FutsalBookingAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'slot', 'player_count', 'status', 'payment_method', 'has_proof', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'slot__date']
    search_fields = ['contact_name', 'contact_email']
    readonly_fields = ['created_at', 'updated_at', 'proof_image']

    def has_proof(self, obj):
        return bool(obj.proof_image)
    has_proof.boolean = True