from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ItikafProgram(models.Model):
    """Iʿtikāf Program - Spiritual retreat program in the mosque"""
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male Only'),
        ('female', 'Female Only'),
        ('both', 'Both'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Dates and timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    
    # Location and capacity
    location = models.CharField(max_length=200, default='Main Prayer Hall')
    capacity = models.PositiveIntegerField()
    gender_restriction = models.CharField(max_length=10, choices=GENDER_CHOICES, default='both')
    
    # Program details
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=True)
    requirements = models.TextField(blank=True, help_text='Requirements for participants')
    what_to_bring = models.TextField(blank=True, help_text='What participants should bring')
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    image = models.ImageField(upload_to='itikaf/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Organizer
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_itikaf_programs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Iʿtikāf Program'
        verbose_name_plural = 'Iʿtikāf Programs'
    
    def __str__(self):
        return self.title
    
    def get_image_url(self):
        """Return the image URL - either from uploaded file or external URL"""
        if self.image:
            return self.image.url
        return self.image_url
    
    @property
    def participant_count(self):
        """Get the number of confirmed participants"""
        try:
            if self.pk:
                return self.registrations.filter(status='confirmed').count()
            return 0
        except Exception:
            return 0
    
    @property
    def is_registration_open(self):
        """Check if registration is still open"""
        try:
            from django.utils import timezone
            if not self.registration_deadline:
                return False
            return timezone.now() < self.registration_deadline and self.status == 'upcoming'
        except Exception:
            return False
    
    @property
    def is_full(self):
        """Check if program is at capacity"""
        try:
            if not self.capacity:
                return False
            return self.participant_count >= self.capacity
        except Exception:
            return False


class ItikafSchedule(models.Model):
    """Daily schedule for Iʿtikāf program"""
    
    program = models.ForeignKey(ItikafProgram, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    day_number = models.PositiveIntegerField(help_text='Day number in the program (1, 2, 3, etc.)')
    
    # Daily activities
    fajr_activity = models.CharField(max_length=200, blank=True, default='Fajr Prayer')
    dhuhr_activity = models.CharField(max_length=200, blank=True, default='Dhuhr Prayer')
    asr_activity = models.CharField(max_length=200, blank=True, default='Asr Prayer')
    maghrib_activity = models.CharField(max_length=200, blank=True, default='Maghrib Prayer')
    isha_activity = models.CharField(max_length=200, blank=True, default='Isha Prayer')
    
    # Special activities
    morning_session = models.TextField(blank=True, help_text='Morning session activities')
    afternoon_session = models.TextField(blank=True, help_text='Afternoon session activities')
    evening_session = models.TextField(blank=True, help_text='Evening session activities')
    
    # Meal times
    breakfast_time = models.TimeField(blank=True, null=True)
    lunch_time = models.TimeField(blank=True, null=True)
    dinner_time = models.TimeField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True, help_text='Additional notes for the day')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'day_number']
        unique_together = ['program', 'date']
        verbose_name = 'Iʿtikāf Schedule'
        verbose_name_plural = 'Iʿtikāf Schedules'
    
    def __str__(self):
        return f"{self.program.title} - Day {self.day_number} ({self.date})"


class ItikafRegistration(models.Model):
    """Registration for Iʿtikāf program"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('waitlisted', 'Waitlisted'),
        ('cancelled', 'Cancelled'),
    ]
    
    program = models.ForeignKey(ItikafProgram, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itikaf_registrations')
    
    # Registration details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    special_requirements = models.TextField(blank=True, help_text='Dietary restrictions, medical needs, etc.')
    notes = models.TextField(blank=True, help_text='Additional notes from participant')
    
    # Payment
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('refunded', 'Refunded'),
    ])
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['program', 'user']
        ordering = ['-registered_at']
        verbose_name = 'Iʿtikāf Registration'
        verbose_name_plural = 'Iʿtikāf Registrations'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.program.title}"
