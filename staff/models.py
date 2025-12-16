from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class StaffMember(models.Model):
    ROLE_CHOICES = [
        ('imam', 'Imam'),
        ('teacher', 'Teacher'),
        ('administrator', 'Administrator'),
        ('maintenance', 'Maintenance'),
        ('security', 'Security'),
        ('volunteer', 'Volunteer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    specializations = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"


class StaffAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ]
    
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['staff', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.date}"


class StaffTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),        # Assigned, waiting for staff
        ('accepted', 'Accepted'),      # Staff acknowledged
        ('in_progress', 'In Progress'),# Staff working
        ('submitted', 'Submitted'),    # Staff finished, waiting review
        ('completed', 'Completed'),    # Admin approved
        ('cancelled', 'Cancelled'),    # Removed
        ('rejected', 'Rejected'),      # Admin sent back
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    task = models.TextField()
    assigned_to = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task[:50]} - {self.assigned_to.user.get_full_name()}"