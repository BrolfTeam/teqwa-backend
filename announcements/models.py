from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    # Optional fundraising link
    donation_cause = models.ForeignKey(
        'donations.DonationCause',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements',
        help_text='Optional: Link this announcement to a donation cause for fundraising'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title