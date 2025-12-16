from rest_framework import serializers
from .models import Announcement
from donations.serializers import DonationCauseSerializer


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    donation_cause_details = DonationCauseSerializer(source='donation_cause', read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'author', 'author_name', 'tags', 'featured', 'published',
            'donation_cause', 'donation_cause_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)