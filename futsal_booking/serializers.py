from rest_framework import serializers
from .models import FutsalSlot, FutsalBooking


class FutsalSlotSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    
    class Meta:
        model = FutsalSlot
        fields = ['id', 'date', 'start_time', 'end_time', 'time', 'location', 
                 'price', 'max_players', 'available', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_time(self, obj):
        return f"{obj.start_time.strftime('%H:%M')}-{obj.end_time.strftime('%H:%M')}"


class FutsalBookingSerializer(serializers.ModelSerializer):
    slot_info = FutsalSlotSerializer(source='slot', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = FutsalBooking
        fields = ['id', 'slot', 'slot_info', 'user', 'user_name', 'contact_name', 
                 'contact_email', 'contact_phone', 'player_count', 'status', 
                 'agree_to_rules', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)