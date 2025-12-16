from rest_framework import serializers
from .models import MembershipTier, UserMembership

class MembershipTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipTier
        fields = ['id', 'name', 'slug', 'description', 'price', 'benefits', 'color', 'icon', 'is_featured']

class UserMembershipSerializer(serializers.ModelSerializer):
    tier_details = MembershipTierSerializer(source='tier', read_only=True)

    class Meta:
        model = UserMembership
        fields = ['id', 'user', 'tier', 'tier_details', 'status', 'start_date', 'expiry_date', 'last_payment_date', 'auto_renew']
        read_only_fields = ['user', 'status', 'start_date', 'expiry_date', 'last_payment_date']
