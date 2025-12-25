from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class MembershipTier(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly price in ETB")
    benefits = models.JSONField(default=list, help_text="List of benefits as strings")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Visual/UI fields
    color = models.CharField(max_length=50, default='emerald', help_text="UI theme color name (e.g., emerald, amber, purple)")
    icon = models.CharField(max_length=50, default='FiStar', help_text="React Icon name")
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.price} ETB)"

    class Meta:
        ordering = ['price']


class UserMembership(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
        ('pending', 'Pending Payment'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    tier = models.ForeignKey(MembershipTier, on_delete=models.PROTECT, related_name='members')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)

    # Payment fields
    payment_method = models.CharField(max_length=20, choices=[
        ('card', 'Credit Card (Chapa)'),
        ('manual_qr', 'Manual Transfer / QR Code'),
        ('cash', 'Cash'),
    ], default='card')
    proof_image = models.ImageField(upload_to='memberships/proofs/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.tier.name} ({self.status})"
