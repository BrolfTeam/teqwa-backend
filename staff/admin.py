from django.contrib import admin
from .models import StaffMember, StaffAttendance, StaffTask


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'active', 'joined_date']
    list_filter = ['role', 'active', 'joined_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'status', 'total_hours']
    list_filter = ['status', 'date']
    search_fields = ['staff__user__username']


@admin.register(StaffTask)
class StaffTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'assigned_to', 'priority', 'status', 'due_date']
    list_filter = ['priority', 'status', 'due_date']
    search_fields = ['task', 'assigned_to__user__username']