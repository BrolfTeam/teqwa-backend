from rest_framework import serializers
from .models import StaffMember, StaffAttendance, StaffTask


class StaffMemberSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = StaffMember
        fields = ['id', 'name', 'email', 'phone', 'role', 'bio', 'specializations', 
                 'languages', 'active', 'joined_date']
        read_only_fields = ['id', 'joined_date']


class StaffAttendanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)
    staff_id = serializers.IntegerField(source='staff.id', read_only=True)

    class Meta:
        model = StaffAttendance
        fields = ['id', 'staff', 'staff_id', 'staff_name', 'date', 'check_in', 'check_out', 
                 'total_hours', 'status', 'notes']
        read_only_fields = ['id']


class StaffTaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.user.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    due_date = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = StaffTask
        fields = ['id', 'task', 'assigned_to', 'assigned_to_name', 
                 'assigned_by', 'assigned_by_name', 'priority', 'status', 'due_date', 
                 'started_at', 'submitted_at', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'assigned_by', 'started_at', 'submitted_at', 'completed_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)