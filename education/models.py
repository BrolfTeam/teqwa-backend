from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EducationalService(models.Model):
    SERVICE_TYPES = [
        ('daily_qirat', 'Daily Qirat Program'),
        ('community_quran', 'Community Quran Reading'),
        ('friday_khutba', 'Friday Khutba'),
        ('quran_recitation', 'Quran Recitation (Qirat)'),
        ('quran_memorization', 'Quran Memorization (Hifz)'),
        ('arabic_language', 'Arabic Language'),
        ('islamic_studies', 'Islamic Studies'),
        ('tajweed', 'Tajweed'),
        ('fiqh', 'Fiqh (Islamic Jurisprudence)'),
        ('hadith', 'Hadith Studies'),
        ('tafseer', 'Tafseer (Quran Interpretation)'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('children', 'Children (6-12)'),
        ('teens', 'Teens (13-17)'),
        ('adults', 'Adults (18+)'),
        ('seniors', 'Seniors (60+)'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('full', 'Full'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_services')
    schedule = models.CharField(max_length=200)
    duration = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_service_type_display()}"

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='confirmed').count()


class ServiceEnrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    service = models.ForeignKey(EducationalService, on_delete=models.CASCADE, related_name='enrollments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['service', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.service.title}"


class Lecture(models.Model):
    SUBJECT_CHOICES = [
        ('quran_recitation', 'Quran Recitation'),
        ('tafseer', 'Tafseer'),
        ('hadith', 'Hadith'),
        ('fiqh', 'Fiqh'),
        ('seerah', 'Seerah'),
        ('aqidah', 'Aqidah'),
        ('general', 'General Lecture'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lectures')
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='general')
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Video URL")
    video_file = models.FileField(upload_to='lectures/videos/', blank=True, null=True, help_text="Upload local video file")
    audio_file = models.FileField(upload_to='lectures/audio/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='lectures/thumbnails/', blank=True, null=True)
    date_recorded = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return self.title