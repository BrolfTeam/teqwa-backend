from rest_framework import serializers
from .models import ItikafProgram, ItikafSchedule, ItikafRegistration


class ItikafScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Iʿtikāf daily schedule"""
    
    class Meta:
        model = ItikafSchedule
        fields = [
            'id', 'program', 'date', 'day_number',
            'fajr_activity', 'dhuhr_activity', 'asr_activity', 
            'maghrib_activity', 'isha_activity',
            'morning_session', 'afternoon_session', 'evening_session',
            'breakfast_time', 'lunch_time', 'dinner_time',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ItikafProgramSerializer(serializers.ModelSerializer):
    """Serializer for Iʿtikāf program"""
    
    participant_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    image = serializers.SerializerMethodField()
    schedules = ItikafScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = ItikafProgram
        fields = [
            'id', 'title', 'description', 'short_description',
            'start_date', 'end_date', 'registration_deadline',
            'location', 'capacity', 'gender_restriction',
            'fee', 'is_free', 'requirements', 'what_to_bring',
            'status', 'image', 'image_url',
            'organizer', 'organizer_name',
            'participant_count', 'is_registration_open', 'is_full',
            'schedules', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
    
    def get_image(self, obj):
        """Return the absolute image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_url
    
    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class ItikafRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for Iʿtikāf registration"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    program_title = serializers.CharField(source='program.title', read_only=True)
    program_start_date = serializers.DateTimeField(source='program.start_date', read_only=True)
    program_end_date = serializers.DateTimeField(source='program.end_date', read_only=True)
    
    class Meta:
        model = ItikafRegistration
        fields = [
            'id', 'program', 'user', 'user_name', 'user_email',
            'program_title', 'program_start_date', 'program_end_date',
            'status', 'emergency_contact', 'emergency_phone',
            'special_requirements', 'notes',
            'special_requirements', 'notes',
            'payment_status', 'payment_amount', 'payment_method', 'proof_image',
            'registered_at', 'confirmed_at', 'cancelled_at'
        ]
        read_only_fields = ['id', 'user', 'registered_at', 'confirmed_at', 'cancelled_at']


class ItikafRegistrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Iʿtikāf registration"""
    
    class Meta:
        model = ItikafRegistration
        fields = [
            'program', 'emergency_contact', 'emergency_phone',
            'special_requirements', 'notes'
        ]

