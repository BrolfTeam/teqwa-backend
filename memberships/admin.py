from django.contrib import admin
from .models import MembershipTier, UserMembership

@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'is_featured')
    search_fields = ('name',)
    list_filter = ('is_active', 'is_featured')

@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'status', 'start_date', 'expiry_date')
    search_fields = ('user__username', 'user__email')
    list_filter = ('status', 'tier')
