from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Student, Parent, Course, Timetable, Assignment, Exam,
    Submission, Grade, StudentMessage, Announcement
)
from education.models import EducationalService

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'student_id', 'parent', 'parent_name',
            'date_of_birth', 'grade_level', 'enrollment_date',
            'is_active', 'emergency_contact', 'emergency_phone',
            'medical_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }

    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.get_full_name()
        return None


class ParentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Parent
        fields = [
            'id', 'user', 'relationship', 'phone', 'address',
            'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }

    def get_children(self, obj):
        children = Student.objects.filter(parent=obj.user)
        return StudentSerializer(children, many=True).data


class CourseSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'service', 'code', 'credits', 'instructor_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_service(self, obj):
        from education.serializers import EducationalServiceSerializer
        return EducationalServiceSerializer(obj.service).data

    def get_instructor_name(self, obj):
        if obj.service.instructor:
            return obj.service.instructor.get_full_name()
        return None


class TimetableSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Timetable
        fields = [
            'id', 'course', 'day', 'start_time', 'end_time',
            'location', 'instructor', 'instructor_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_instructor_name(self, obj):
        if obj.instructor:
            return obj.instructor.get_full_name()
        return None


class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    instructor_name = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'title', 'description', 'assignment_type',
            'instructor', 'instructor_name', 'due_date', 'max_score',
            'instructions', 'attachments', 'is_published', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


    def get_instructor_name(self, obj):
        if obj.instructor:
            return obj.instructor.get_full_name()
        return None


class ExamSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'course', 'title', 'description', 'instructor', 'instructor_name',
            'exam_date', 'duration_minutes', 'max_score', 'location',
            'instructions', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_instructor_name(self, obj):
        if obj.instructor:
            return obj.instructor.get_full_name()
        return None


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    is_late = serializers.ReadOnlyField()

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'student', 'content', 'files',
            'status', 'submitted_at', 'is_late', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GradeSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    graded_by_name = serializers.SerializerMethodField()
    percentage = serializers.ReadOnlyField()
    letter_grade = serializers.ReadOnlyField()

    class Meta:
        model = Grade
        fields = [
            'id', 'submission', 'exam', 'student', 'score', 'max_score',
            'feedback', 'graded_by', 'graded_by_name', 'percentage',
            'letter_grade', 'graded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'graded_at', 'updated_at']

    def get_graded_by_name(self, obj):
        if obj.graded_by:
            return obj.graded_by.get_full_name()
        return None


class StudentMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    course = CourseSerializer(read_only=True)

    class Meta:
        model = StudentMessage
        fields = [
            'id', 'sender', 'recipient', 'subject', 'message',
            'is_read', 'read_at', 'course', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_sender(self, obj):
        return {
            'id': obj.sender.id,
            'username': obj.sender.username,
            'email': obj.sender.email,
            'full_name': obj.sender.get_full_name(),
        }

    def get_recipient(self, obj):
        return {
            'id': obj.recipient.id,
            'username': obj.recipient.username,
            'email': obj.recipient.email,
            'full_name': obj.recipient.get_full_name(),
        }


class AnnouncementSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'author', 'course', 'priority',
            'is_published', 'published_at', 'expires_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'full_name': obj.author.get_full_name(),
        }

