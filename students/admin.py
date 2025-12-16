from django.contrib import admin
from .models import (
    Student, Parent, Course, Timetable, Assignment, Exam,
    Submission, Grade, StudentMessage, Announcement
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'grade_level', 'parent', 'is_active', 'enrollment_date']
    list_filter = ['is_active', 'grade_level', 'enrollment_date']
    search_fields = ['student_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'enrollment_date']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'student_id', 'grade_level', 'date_of_birth', 'is_active')
        }),
        ('Parent/Guardian (Optional)', {
            'fields': ('parent',),
            'description': 'Link a parent user if applicable. The parent user must have role="parent".'
        }),
        ('Emergency Information', {
            'fields': ('emergency_contact', 'emergency_phone', 'medical_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('enrollment_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make parent field optional and show helpful text
        if 'parent' in form.base_fields:
            form.base_fields['parent'].required = False
            form.base_fields['parent'].help_text = 'Optional: Select a user to link as parent/guardian. You can select any user - if they don\'t have a Parent profile, create one in the Parent admin.'
            # Show all users, not just those with parent role
            from django.contrib.auth import get_user_model
            User = get_user_model()
            form.base_fields['parent'].queryset = User.objects.all().order_by('username')
        return form


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['user', 'relationship', 'phone', 'created_at']
    list_filter = ['relationship', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'relationship'),
            'description': 'Select a user and specify their relationship. The user should have role="parent".'
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Allow selecting any user - we'll auto-update their role
        if 'user' in form.base_fields:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            form.base_fields['user'].queryset = User.objects.all().order_by('username')
            form.base_fields['user'].help_text = 'Select any user. Their role will be automatically set to "parent" when you save.'
        return form
    
    def save_model(self, request, obj, form, change):
        """Ensure user has parent role when creating parent profile"""
        # Save the parent first
        super().save_model(request, obj, form, change)
        # Auto-update user role to parent if not already set
        if obj.user.role != 'parent':
            obj.user.role = 'parent'
            obj.user.save()
            self.message_user(request, f'✅ Parent created successfully! User "{obj.user.username}" role has been automatically updated to "parent".', level='success')
        else:
            self.message_user(request, f'✅ Parent created successfully!', level='success')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'service', 'credits']
    search_fields = ['code', 'service__title']
    readonly_fields = ['created_at']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['course', 'day', 'start_time', 'end_time', 'instructor', 'location']
    list_filter = ['day', 'course']
    search_fields = ['course__code', 'instructor__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'instructor', 'due_date', 'is_published', 'max_score']
    list_filter = ['is_published', 'assignment_type', 'due_date']
    search_fields = ['title', 'course__code', 'instructor__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'instructor', 'exam_date', 'is_published', 'max_score']
    list_filter = ['is_published', 'exam_date']
    search_fields = ['title', 'course__code', 'instructor__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'status', 'submitted_at', 'created_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['assignment__title', 'student__user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'score', 'max_score', 'percentage', 'letter_grade', 'graded_by', 'graded_at']
    list_filter = ['graded_at']
    search_fields = ['student__user__username', 'graded_by__username']
    readonly_fields = ['graded_at', 'updated_at']


@admin.register(StudentMessage)
class StudentMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['subject', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'course', 'priority', 'is_published', 'published_at']
    list_filter = ['is_published', 'priority', 'published_at']
    search_fields = ['title', 'author__username']
    readonly_fields = ['created_at', 'updated_at']

