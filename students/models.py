from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Student(models.Model):
    """Student profile linked to User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True, help_text="Unique student ID")
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children', help_text="Optional: Link a parent/guardian user")
    date_of_birth = models.DateField(null=True, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    medical_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class Parent(models.Model):
    """Parent profile linked to User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile', help_text="Select a user. Their role will be set to 'parent' automatically.")
    relationship = models.CharField(max_length=50, help_text="e.g., Father, Mother, Guardian")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parent/Guardian"
        verbose_name_plural = "Parents/Guardians"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.relationship}"
    
    def save(self, *args, **kwargs):
        """Auto-set user role to parent when saving"""
        super().save(*args, **kwargs)
        if self.user.role != 'parent':
            self.user.role = 'parent'
            self.user.save(update_fields=['role'])


class Course(models.Model):
    """Course linked to EducationalService"""
    service = models.OneToOneField('education.EducationalService', on_delete=models.CASCADE, related_name='course')
    code = models.CharField(max_length=20, unique=True)
    credits = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.service.title}"


class Timetable(models.Model):
    """Class timetable/schedule"""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timetable_entries')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='timetable_classes', limit_choices_to={'role__in': ['teacher', 'staff']})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day', 'start_time']
        unique_together = ['course', 'day', 'start_time']

    def __str__(self):
        return f"{self.course.code} - {self.get_day_display()} {self.start_time}"


class Assignment(models.Model):
    """Assignment for students"""
    TYPE_CHOICES = [
        ('homework', 'Homework'),
        ('project', 'Project'),
        ('essay', 'Essay'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='homework')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments', limit_choices_to={'role__in': ['teacher', 'staff']})
    due_date = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)
    instructions = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True, help_text="List of file URLs")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.title} - {self.course.code}"

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date and not self.is_published


class Exam(models.Model):
    """Exam/Test for students"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams', limit_choices_to={'role__in': ['teacher', 'staff']})
    exam_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    max_score = models.PositiveIntegerField(default=100)
    location = models.CharField(max_length=200, blank=True)
    instructions = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-exam_date']

    def __str__(self):
        return f"{self.title} - {self.course.code}"


class Submission(models.Model):
    """Student submission for assignments"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('late', 'Late'),
        ('graded', 'Graded'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField(blank=True)
    files = models.JSONField(default=list, blank=True, help_text="List of file URLs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at', '-created_at']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.assignment.title}"

    @property
    def is_late(self):
        if self.submitted_at and self.assignment.due_date:
            return self.submitted_at > self.assignment.due_date
        return False


class Grade(models.Model):
    """Grades for assignments and exams"""
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='grade', null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.PositiveIntegerField()
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_items', limit_choices_to={'role__in': ['teacher', 'staff']})
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-graded_at']
        unique_together = [['submission', 'student'], ['exam', 'student']]

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.score}/{self.max_score}"

    @property
    def percentage(self):
        if self.max_score > 0:
            return (float(self.score) / self.max_score) * 100
        return 0

    @property
    def letter_grade(self):
        pct = self.percentage
        if pct >= 90:
            return 'A'
        elif pct >= 80:
            return 'B'
        elif pct >= 70:
            return 'C'
        elif pct >= 60:
            return 'D'
        else:
            return 'F'


class StudentMessage(models.Model):
    """Messages between students and teachers"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.get_full_name()} to {self.recipient.get_full_name()} - {self.subject}"


class Announcement(models.Model):
    """Announcements for students"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_announcements', limit_choices_to={'role__in': ['teacher', 'staff', 'admin']})
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

