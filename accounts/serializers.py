from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, UserSession, UserActivity

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'gender', 'address', 'emergency_contact', 
                 'emergency_phone', 'occupation', 'education_level', 'interests', 
                 'bio', 'notification_preferences', 'privacy_settings', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                 'phone', 'avatar', 'is_verified', 'created_at', 'profile']
        read_only_fields = ['id', 'created_at', 'is_verified', 'username']


class UserSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserSession
        fields = ['id', 'user', 'user_name', 'ip_address', 'user_agent', 
                 'device_info', 'location', 'is_active', 'last_activity', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ['id', 'activity_type', 'activity_type_display', 'description', 
                 'ip_address', 'user_agent', 'metadata', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class UpdateProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance