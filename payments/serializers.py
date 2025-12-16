from rest_framework import serializers
from .models import Transaction

class InitializePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='ETB')
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    
    # Generic relation fields
    content_type_model = serializers.CharField(help_text="Model name for generic relation (e.g., 'donation', 'futsalbooking')")
    object_id = serializers.IntegerField()

    def validate(self, data):
        # Additional validation logic if needed
        return data

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
