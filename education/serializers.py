from rest_framework import serializers
from .models import EducationalService, Course, ServiceEnrollment, Lecture


class EducationalServiceSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    enrolled_count = serializers.ReadOnlyField()
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)

    class Meta:
        model = EducationalService
        fields = ['id', 'title', 'description', 'service_type', 'service_type_display',
                 'instructor', 'instructor_name', 'schedule', 'duration', 'capacity', 
                 'enrolled_count', 'level', 'age_group', 'fee', 'status', 
                 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    enrolled_count = serializers.ReadOnlyField()
    service_title = serializers.CharField(source='service.title', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'service', 'service_title', 'title', 'description', 
                 'instructor', 'instructor_name', 'schedule', 'duration', 'capacity', 
                 'enrolled_count', 'level', 'age_group', 'fee', 'status', 
                 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceEnrollmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    service_title = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)

    class Meta:
        model = ServiceEnrollment
        fields = ['id', 'service', 'course', 'user', 'user_name', 'service_title', 
                 'service_type', 'course_title', 'status', 'payment_status', 
                 'enrollment_date', 'notes']
        read_only_fields = ['id', 'user', 'enrollment_date']
    
    def get_service_title(self, obj):
        if obj.course:
            return obj.course.service.title
        return obj.service.title if obj.service else None
    
    def get_service_type(self, obj):
        if obj.course:
            return obj.course.service.service_type
        return obj.service.service_type if obj.service else None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        if not data.get('course') and not data.get('service'):
            raise serializers.ValidationError('Either course or service must be provided')
        return data


class LectureSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    instructor_avatar = serializers.CharField(source='instructor.avatar', read_only=True, allow_null=True)
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)

    class Meta:
        model = Lecture
        fields = ['id', 'title', 'description', 'instructor', 'instructor_name', 
                 'instructor_avatar', 'subject', 'subject_display', 'video_url', 'video_file',
                 'audio_file', 'thumbnail', 'date_recorded', 'created_at']
        read_only_fields = ['id', 'created_at']