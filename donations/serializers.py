from rest_framework import serializers
from django.conf import settings
from .models import Donation, DonationCause


class DonationCauseSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = DonationCause
        fields = ['id', 'title', 'description', 'target_amount', 'raised_amount', 
                 'currency', 'status', 'end_date', 'image', 'progress_percentage', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'raised_amount', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """Override to convert image path to full URL"""
        representation = super().to_representation(instance)
        
        # Convert image path to full URL
        if representation.get('image'):
            image_url = self._get_full_image_url(instance.image)
            # Only set if we got a valid URL, otherwise keep None
            representation['image'] = image_url if image_url else None
        else:
            representation['image'] = None
            
        return representation
    
    def _get_full_image_url(self, image_path):
        """Return full URL for image if it exists"""
        if not image_path:
            return None
        
        # Strip any whitespace
        image_path = str(image_path).strip()
        if not image_path:
            return None
        
        # If it's a data URL (base64 encoded image), validate and return as-is
        if image_path.startswith('data:'):
            # Basic validation: check if it looks like a valid data URL
            # Format: data:[<mediatype>][;base64],<data>
            if ';base64,' in image_path or image_path.startswith('data:image/'):
                # Check if data URL appears truncated (common issue with CharField max_length limits)
                # Base64 data URLs should end with valid base64 characters (not with incomplete strings)
                # This is a basic check - full validation would be more complex
                return image_path
            else:
                # Invalid data URL format, return None to show fallback
                return None
        
        # If already a full URL, return as is
        if image_path.startswith('http://') or image_path.startswith('https://'):
            return image_path
        
        # Get request from context to build absolute URL
        request = self.context.get('request')
        if request:
            # If MEDIA_URL is already absolute (S3), use it directly
            if settings.MEDIA_URL.startswith('http'):
                # For S3 or absolute URLs, just append the image path
                return f"{settings.MEDIA_URL.rstrip('/')}/{image_path.lstrip('/')}"
            else:
                # For relative MEDIA_URL, build absolute URL using request
                return request.build_absolute_uri(f"{settings.MEDIA_URL}{image_path.lstrip('/')}")
        
        # Fallback: construct URL from settings
        media_url = settings.MEDIA_URL
        if media_url.startswith('http'):
            # Already absolute (S3 or CDN)
            return f"{media_url.rstrip('/')}/{image_path.lstrip('/')}"
        else:
            # Relative URL - construct base URL
            if hasattr(settings, 'BASE_URL'):
                base_url = settings.BASE_URL
            else:
                base_url = 'http://localhost:8000' if settings.DEBUG else ''
            
            return f"{base_url.rstrip('/')}{media_url.rstrip('/')}/{image_path.lstrip('/')}"


class DonationSerializer(serializers.ModelSerializer):
    cause_title = serializers.CharField(source='cause.title', read_only=True)

    class Meta:
        model = Donation
        fields = ['id', 'donor_name', 'email', 'amount', 'currency', 'method', 
                 'message', 'cause', 'cause_title', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set user if authenticated
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)
